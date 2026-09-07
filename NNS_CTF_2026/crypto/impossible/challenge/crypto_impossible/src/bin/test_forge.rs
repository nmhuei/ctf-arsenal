use impossible_player::*;
use bellman::groth16::{Proof as BellmanProof, VerifyingKey};
use pairing::bls12_381::{Bls12, Fr};
use pairing::{CurveAffine, CurveProjective, Field, PrimeField};
use std::fs::File;
use std::path::Path;

fn main() {
    let manifest_dir = env!("CARGO_MANIFEST_DIR");
    let vk_path = Path::new(manifest_dir).join("vk.bin");
    let mut file = File::open(vk_path).expect("open vk.bin");
    let vk = VerifyingKey::<Bls12>::read(&mut file).expect("read vk");
    
    let ceremony_id = "3c311d9dfb7735e42643f394dc2c10af".to_string();
    let tau_str = "3894627051107121998319229043008213446770981528672674568925122813412699817";
    let tau = Fr::from_str(tau_str).expect("tau");
    
    let [_alpha, _beta, gamma, delta, _g1_scale, _g2_scale] = derive(tau);
    
    let pub_vk = Public {
        ceremony_id: ceremony_id.clone(),
        vk: vk.clone(),
    };
    
    let claim_fr = fr(CLAIM);
    let mut acc = vk.ic[0].into_projective();
    let mut term1 = vk.ic[1].into_projective();
    term1.mul_assign(claim_fr);
    acc.add_assign(&term1);
    
    let mut gamma_delta_inv = gamma;
    gamma_delta_inv.mul_assign(&delta.inverse().unwrap());
    
    let mut c_proj = acc;
    c_proj.mul_assign(gamma_delta_inv);
    c_proj.negate();
    
    let a_affine = vk.alpha_g1;
    let b_affine = vk.beta_g2;
    let c_affine = c_proj.into_affine();
    
    let proof = Proof {
        ceremony_id: ceremony_id.clone(),
        claim: CLAIM,
        inner: BellmanProof {
            a: a_affine,
            b: b_affine,
            c: c_affine,
        },
    };
    
    let ok = verify(&pub_vk, &proof);
    if ok {
        println!("FORGERY SUCCESS: true");
        println!("PROOF STRING: {}", encode_proof(&proof));
    } else {
        eprintln!("Verification failed!");
        std::process::exit(1);
    }
}
