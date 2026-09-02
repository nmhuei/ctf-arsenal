import express, {Request, Response as ExpressResponse} from 'express';
import bodyParser from 'body-parser';
import {
    proxyLocalchainRequest,
    SessionLifecycleError,
    startLocalchainSessionReaper,
} from './localchain';
import { startNcServer } from './server';

const FLAG = process.env.FLAG || 'ctf{test-flag}';
const PORT = Number(process.env.PORT || '3000');
const NC_PORT = Number(process.env.NC_PORT || '1337');

const app = express();

function extractProxyBody(req: Request): string | ArrayBuffer | undefined {
    if (req.method === 'GET' || req.method === 'HEAD') {
        return undefined;
    }

    if (Buffer.isBuffer(req.body)) {
        if (req.body.length === 0) {
            return undefined;
        }

        const copy = new Uint8Array(req.body.byteLength);
        copy.set(req.body);
        return copy.buffer;
    }

    if (typeof req.body === 'string') {
        return req.body.length > 0 ? req.body : undefined;
    }

    if (req.body && typeof req.body === 'object') {
        return JSON.stringify(req.body);
    }

    return undefined;
}

async function pipeProxyResponse(res: ExpressResponse, upstream: globalThis.Response) {
    res.status(upstream.status);

    const contentType = upstream.headers.get('content-type');
    if (contentType) {
        res.setHeader('content-type', contentType);
    }

    const cacheControl = upstream.headers.get('cache-control');
    if (cacheControl) {
        res.setHeader('cache-control', cacheControl);
    }

    res.send(Buffer.from(await upstream.arrayBuffer()));
}

async function handleSessionApiV2Proxy(req: Request, res: ExpressResponse) {
    try {
        const upstream = await proxyLocalchainRequest(req.params.uuid, 'api-v2', req.url, {
            method: req.method,
            headers: {
                'content-type': req.get('content-type') || 'application/json',
            },
            body: extractProxyBody(req),
        });
        await pipeProxyResponse(res, upstream);
    } catch (error) {
        respondWithError(res, error, 'proxy request failed');
    }
}

app.use('/instance/:uuid/api/v2', bodyParser.raw({ type: '*/*', limit: '10mb' }), handleSessionApiV2Proxy);

app.use(bodyParser.json());

function respondWithError(res: ExpressResponse, error: unknown, fallbackMessage: string) {
    if (error instanceof SessionLifecycleError) {
        res.status(error.statusCode).json({ success: false, error: error.message });
        return;
    }

    res.status(500).json({ success: false, error: fallbackMessage });
}

startLocalchainSessionReaper();
startNcServer({
    port: NC_PORT,
    flag: FLAG,
});

app.listen(PORT, () => {
    console.log(`HTTP server listening on port ${PORT}`);
});
