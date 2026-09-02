import { SuiJsonRpcClient } from "@mysten/sui/jsonRpc";
import { Transaction } from "@mysten/sui/transactions";
import { Ed25519Keypair } from "@mysten/sui/keypairs/ed25519";
import { fromBase64, fromHex, toHex } from "@mysten/sui/utils";
import { bcs } from "@mysten/sui/bcs";
import { execSync } from "child_process";

const PORTAL_URL = "http://34.2.147.230:8501";

async function solve() {
    console.log("[*] Checking portal status...");
    let statusRes = await fetch(`${PORTAL_URL}/status`);
    let cookie = statusRes.headers.get("set-cookie") || "";
    
    let launchSuccess = false;
    for (let attempt = 1; attempt <= 10; attempt++) {
        console.log(`[*] Launch attempt ${attempt}...`);
        let challRes = await fetch(`${PORTAL_URL}/challenge`, { headers: { "Cookie": cookie } });
        let challData = await challRes.json();
        let setCookie = challRes.headers.get("set-cookie");
        if (setCookie) cookie = setCookie;
        
        let challStr = challData.challenge;
        console.log(`[*] Solving PoW: ${challStr}...`);
        let sol = execSync(`curl -sSfL https://pwn.red/pow | sh -s ${challStr}`, { encoding: "utf-8" }).trim();
        
        let solRes = await fetch(`${PORTAL_URL}/solution`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Cookie": cookie },
            body: JSON.stringify({ solution: sol })
        });
        console.log("PoW submission:", await solRes.json());
        
        let launchRes = await fetch(`${PORTAL_URL}/launch`, {
            method: "POST",
            headers: { "Cookie": cookie }
        });
        let launchData = await launchRes.json();
        console.log("Launch response:", JSON.stringify(launchData, null, 2));
        
        if (launchData.success || launchData["0"]) {
            launchSuccess = true;
            break;
        }
        await new Promise(r => setTimeout(r, 3000));
    }

    if (!launchSuccess) {
        throw new Error("Failed to launch instance");
    }

    let dataRes = await fetch(`${PORTAL_URL}/data`, { headers: { "Cookie": cookie } });
    let data = await dataRes.json();
    console.log("Instance Data:\n", JSON.stringify(data, null, 2));

    let rpcUrl = null;
    let privKeyStr = null;
    let packageId = null;

    for (let [k, v] of Object.entries(data)) {
        if (typeof v === "object" && v !== null) {
            let subK = Object.keys(v)[0];
            let subV = String(Object.values(v)[0]).replace(/{ORIGIN}/g, PORTAL_URL);
            if (subK.toLowerCase().includes("rpc") || subV.startsWith("http")) {
                rpcUrl = subV;
            } else if (subK.toLowerCase().includes("priv") || subK.toLowerCase().includes("key")) {
                privKeyStr = subV;
            } else if (subK.toLowerCase().includes("package") || subK.toLowerCase().includes("contract")) {
                packageId = subV;
            }
        }
    }

    console.log(`RPC URL: ${rpcUrl}`);
    console.log(`Private Key: ${privKeyStr}`);
    console.log(`Package ID: ${packageId}`);

    const client = new SuiJsonRpcClient({ url: rpcUrl });
    
    let keypair;
    if (privKeyStr.startsWith("suiprivkey")) {
        keypair = Ed25519Keypair.fromSecretKey(privKeyStr);
    } else if (privKeyStr.length === 64 || privKeyStr.length === 66) {
        let hex = privKeyStr.startsWith("0x") ? privKeyStr.slice(2) : privKeyStr;
        keypair = Ed25519Keypair.fromSecretKey(fromHex(hex));
    } else {
        keypair = Ed25519Keypair.fromSecretKey(fromBase64(privKeyStr));
    }
    
    const playerAddr = keypair.toSuiAddress();
    console.log(`Player Address: ${playerAddr}`);

    console.log("[*] Querying player owned objects...");
    const owned = await client.getOwnedObjects({
        owner: playerAddr,
        options: { showType: true, showContent: true }
    });
    console.log("Owned objects:", JSON.stringify(owned.data, null, 2));

    let operatorAccountId = null;
    for (let obj of owned.data) {
        if (obj.data?.type?.includes("OperatorAccount")) {
            operatorAccountId = obj.data.objectId;
        }
    }
    console.log(`OperatorAccount ID: ${operatorAccountId}`);

    if (!packageId && operatorAccountId) {
        let typeStr = owned.data.find(o => o.data.objectId === operatorAccountId)?.data?.type;
        packageId = typeStr.split("::")[0];
        console.log(`Discovered Package ID: ${packageId}`);
    }

    return { client, keypair, cookie, packageId, operatorAccountId };
}

solve().catch(console.error);
