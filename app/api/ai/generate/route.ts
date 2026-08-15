import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

const OPENAI_URL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';
const NVIDIA_URL = process.env.NVIDIA_BASE_URL || 'https://integrate.api.nvidia.com/v1';
const MAX_PROMPT_CHARS = 24000;
const MAX_OUTPUT_TOKENS = 2048;
const TIMEOUT_MS = 15000;

type Provider = 'openai' | 'nvidia';

type ChatMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

function providerOrder(): Provider[] {
  const configured = (process.env.INTELLIHIRE_AI_PROVIDER_ORDER || 'openai,nvidia')
    .split(',')
    .map((value) => value.trim().toLowerCase())
    .filter((value): value is Provider => value === 'openai' || value === 'nvidia');

  return Array.from(new Set(configured));
}

function providerConfig(provider: Provider) {
  if (provider === 'openai') {
    return {
      key: process.env.OPENAI_API_KEY,
      model: process.env.OPENAI_MODEL,
      baseUrl: OPENAI_URL,
    };
  }

  return {
    key: process.env.NVIDIA_API_KEY,
    model: process.env.NVIDIA_MODEL,
    baseUrl: NVIDIA_URL,
  };
}

function retryable(status: number) {
  return status === 408 || status === 429 || status >= 500;
}

async function requestProvider(provider: Provider, messages: ChatMessage[], maxTokens: number) {
  const config = providerConfig(provider);
  if (!config.key || !config.model) {
    throw new Error(`${provider} is not configured`);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${config.baseUrl.replace(/\/$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: config.model,
        messages,
        temperature: 0.2,
        max_tokens: Math.min(Math.max(maxTokens, 1), MAX_OUTPUT_TOKENS),
      }),
      signal: controller.signal,
      cache: 'no-store',
    });

    if (!response.ok) {
      const body = await response.text().catch(() => '');
      const error = new Error(`${provider} returned HTTP ${response.status}`);
      Object.assign(error, { status: response.status, body: body.slice(0, 500) });
      throw error;
    }

    const body = await response.json() as {
      model?: string;
      choices?: Array<{ message?: { content?: string } }>;
      usage?: Record<string, unknown>;
    };

    const content = body.choices?.[0]?.message?.content?.trim();
    if (!content) throw new Error(`${provider} returned an empty response`);

    return {
      provider,
      model: body.model || config.model,
      content,
      usage: body.usage || {},
    };
  } finally {
    clearTimeout(timeout);
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as {
      messages?: ChatMessage[];
      maxTokens?: number;
    };

    if (!Array.isArray(body.messages) || body.messages.length === 0) {
      return NextResponse.json({ error: 'messages must be a non-empty array' }, { status: 400 });
    }

    const messages = body.messages.slice(0, 20).map((message) => ({
      role: message.role,
      content: String(message.content || '').slice(0, MAX_PROMPT_CHARS),
    }));

    if (messages.some((message) => !['system', 'user', 'assistant'].includes(message.role) || !message.content)) {
      return NextResponse.json({ error: 'invalid message payload' }, { status: 400 });
    }

    const attempted: Provider[] = [];
    const failures: string[] = [];

    for (const provider of providerOrder()) {
      attempted.push(provider);
      try {
        const result = await requestProvider(provider, messages, body.maxTokens || 1024);
        return NextResponse.json({
          success: true,
          ...result,
          failover: attempted.length > 1,
          attemptedProviders: attempted,
        });
      } catch (error) {
        const status = Number((error as { status?: number }).status || 0);
        failures.push(`${provider}:${status || 'error'}`);
        if (!retryable(status)) continue;
      }
    }

    return NextResponse.json({
      success: false,
      error: 'All configured AI providers are unavailable',
      attemptedProviders: attempted,
      failures,
    }, { status: 503 });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
