import { serveStatic } from '@hono/node-server/serve-static';
import matter from 'gray-matter';
import { Hono } from 'hono';
import { MAX_SOURCE_LENGTH } from './limits.js';

export const app = new Hono();

app.post('/api/parse', async (context) => {
  let body: { source?: unknown };

  try {
    body = await context.req.json<{ source?: unknown }>();
  } catch {
    return context.json({ error: 'The request body must be valid JSON.' }, 400);
  }

  if (typeof body?.source !== 'string') {
    return context.json({ error: 'The source field must be a string.' }, 400);
  }

  if (body.source.length > MAX_SOURCE_LENGTH) {
    return context.json(
      { error: `Markdown source cannot exceed ${MAX_SOURCE_LENGTH.toLocaleString()} characters.` },
      413,
    );
  }

  try {
    const { data, content } = matter(body.source);
    return context.json({ data, content });
  } catch (error) {
    return context.json(
      { error: error instanceof Error ? error.message : 'Unable to parse frontmatter.' },
      400,
    );
  }
});

if (process.env.NODE_ENV === 'production') {
  app.use('*', serveStatic({ root: './dist' }));
  app.get('*', serveStatic({ path: './dist/index.html' }));
}
