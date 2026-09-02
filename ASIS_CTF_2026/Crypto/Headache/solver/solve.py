#!/usr/bin/env python3
import socket
import json
import hashlib
import time
import numpy as np
from scipy.optimize import least_squares

HOST = "65.109.208.91"
PORT = 1337

NUM_CHANNELS = 3
DIM = 4
NUM_ROUNDS = 7
NUM_QUERIES = 180


def solve_pow(prefix, target_zeros):
    target = "0" * target_zeros
    nonce = 0
    while True:
        n_str = str(nonce)
        h = hashlib.sha256(f"{prefix}{n_str}".encode()).hexdigest()
        if h.startswith(target):
            return n_str
        nonce += 1


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def eval_model(X, A, B):
    X = np.array(X, dtype=np.float64)
    x_tail = X[-1]
    total_energy = 0.0
    for c in range(NUM_CHANNELS):
        microstate_energies = np.einsum("j,jk,ik->i", x_tail, A[c].T, X)
        gauge_shift = np.max(microstate_energies)
        boltzmann_weights = np.exp(microstate_energies - gauge_shift)
        partition_fn = np.sum(boltzmann_weights)
        observables = np.dot(X, B[c])
        ensemble_expectation = np.dot(boltzmann_weights, observables) / partition_fn
        total_energy += float(ensemble_expectation)
    return total_energy


def fit_parameters(queries_u, queries_v, targets):
    delta = queries_u - queries_v
    N = len(delta)

    def fun_and_jac(params):
        A = params[:48].reshape(NUM_CHANNELS, DIM, DIM)
        B = params[48:].reshape(NUM_CHANNELS, DIM)

        preds = np.zeros(N)
        jac = np.zeros((N, 60))

        for c in range(NUM_CHANNELS):
            z_c = np.sum((delta @ A[c]) * queries_v, axis=1)
            sig_c = sigmoid(z_c)
            sig_deriv = sig_c * (1.0 - sig_c)
            dot_B_c = delta @ B[c]

            preds += sig_c * dot_B_c + queries_v @ B[c]

            factor = sig_deriv * dot_B_c
            d_A_c = factor[:, None, None] * (delta[:, :, None] * queries_v[:, None, :])
            jac[:, c * 16 : (c + 1) * 16] = d_A_c.reshape(N, 16)

            d_B_c = sig_c[:, None] * delta + queries_v
            jac[:, 48 + c * 4 : 48 + (c + 1) * 4] = d_B_c

        return preds - targets, jac

    def fun(params):
        return fun_and_jac(params)[0]

    def jac(params):
        return fun_and_jac(params)[1]

    best_res = None
    best_cost = 1e9

    for _ in range(60):
        init_params = np.random.uniform(0.5, 2.0, size=60)
        opt = least_squares(
            fun,
            init_params,
            jac=jac,
            bounds=(0.4, 2.1),
            ftol=1e-15,
            xtol=1e-15,
            gtol=1e-15,
            max_nfev=800,
        )
        if opt.cost < best_cost:
            best_cost = opt.cost
            best_res = opt
        if opt.cost < 1e-14:
            break

    A_est = best_res.x[:48].reshape(NUM_CHANNELS, DIM, DIM)
    B_est = best_res.x[48:].reshape(NUM_CHANNELS, DIM)
    return A_est, B_est, best_cost


def read_json_line(f):
    while True:
        line = f.readline()
        if not line:
            raise EOFError("Server closed connection")
        line = line.strip()
        if not line:
            continue
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
        print(f"[Server] {line}")


def solve():
    print(f"[*] Connecting to {HOST}:{PORT}...")
    s = socket.create_connection((HOST, PORT), timeout=30)
    f = s.makefile("rw", encoding="utf-8")

    pow_req = read_json_line(f)
    prefix = pow_req["prefix"]
    target_zeros = pow_req["difficulty_bits"] // 4
    print(f"[*] Solving PoW (prefix: {prefix}, zeros: {target_zeros})...")
    t0 = time.time()
    nonce = solve_pow(prefix, target_zeros)
    print(f"[+] PoW solved in {time.time() - t0:.2f}s: {nonce}")
    f.write(f"{nonce}\n")
    f.flush()

    pow_resp = read_json_line(f)
    print(f"[*] PoW response: {pow_resp}")
    if pow_resp.get("status") != "pow_ok":
        return None

    flag = None

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n==================== ROUND {round_num}/{NUM_ROUNDS} ====================")
        NUM_QUERIES = 160
        queries_u = np.random.uniform(-2.0, 2.0, size=(NUM_QUERIES, DIM))
        queries_v = np.random.uniform(-2.0, 2.0, size=(NUM_QUERIES, DIM))
        targets = []

        print(f"[*] Sending {NUM_QUERIES} pipelined queries to oracle...")
        t_query_start = time.time()
        batch_payload = "".join(f"eval {json.dumps([queries_u[i].tolist(), queries_v[i].tolist()])}\n" for i in range(NUM_QUERIES))
        f.write(batch_payload)
        f.flush()

        for idx in range(NUM_QUERIES):
            resp = read_json_line(f)
            if resp.get("status") != "ok":
                raise RuntimeError(f"Query error: {resp}")
            targets.append(resp["tag"])

        targets = np.array(targets, dtype=np.float64)
        print(f"[+] Pipelined queries completed in {time.time() - t_query_start:.2f}s.")

        print("[*] Optimizing parameters...")
        t_opt_start = time.time()
        A_est, B_est, cost = fit_parameters(queries_u, queries_v, targets)
        print(f"[+] Optimization finished in {time.time() - t_opt_start:.3f}s with residual cost: {cost:.2e}")

        # If not fully converged, query 60 more points and refit
        while cost > 1e-12:
            print("[!] Cost > 1e-12, gathering 60 additional queries...")
            extra_u = np.random.uniform(-2.0, 2.0, size=(60, DIM))
            extra_v = np.random.uniform(-2.0, 2.0, size=(60, DIM))
            batch = "".join(f"eval {json.dumps([extra_u[i].tolist(), extra_v[i].tolist()])}\n" for i in range(60))
            f.write(batch)
            f.flush()
            extra_targets = []
            for _ in range(60):
                resp = read_json_line(f)
                extra_targets.append(resp["tag"])
            queries_u = np.vstack([queries_u, extra_u])
            queries_v = np.vstack([queries_v, extra_v])
            targets = np.concatenate([targets, np.array(extra_targets, dtype=np.float64)])
            A_est, B_est, cost = fit_parameters(queries_u, queries_v, targets)
            print(f"[+] Refit finished with residual cost: {cost:.2e}")

        # Request challenge
        f.write("challenge\n")
        f.flush()
        chall_data = read_json_line(f)
        if chall_data.get("status") != "challenge":
            raise RuntimeError(f"Unexpected challenge response: {chall_data}")

        test_seqs = chall_data["sequences"]
        predicted_tags = [eval_model(s, A_est, B_est) for s in test_seqs]

        # Send verification
        verify_payload = f"verify {json.dumps(predicted_tags)}\n"
        f.write(verify_payload)
        f.flush()

        round_result = read_json_line(f)
        print(f"[+] Round {round_num} Result: {round_result}")

        if "flag" in round_result:
            flag = round_result["flag"]
            print(f"\n🚩 FLAG RECOVERED: {flag}")
            break

    return flag


if __name__ == "__main__":
    solve()
