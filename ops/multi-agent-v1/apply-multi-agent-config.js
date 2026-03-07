#!/usr/bin/env node
const fs = require('fs');

const configPath = '/data/.openclaw/openclaw.json';
const backupPath = `/data/.openclaw/openclaw.json.bak-multi-agent-v1-${new Date().toISOString().replace(/[:.]/g,'-')}`;

const sandyToken = process.env.DISCORD_TOKEN_SANDY;
const gladosToken = process.env.DISCORD_TOKEN_GLADOS;

if (!sandyToken || !gladosToken) {
  console.error('Missing required env vars: DISCORD_TOKEN_SANDY and/or DISCORD_TOKEN_GLADOS');
  process.exit(1);
}

const raw = fs.readFileSync(configPath, 'utf8');
const cfg = JSON.parse(raw);

// Backup first
fs.writeFileSync(backupPath, raw, 'utf8');

cfg.agents = cfg.agents || {};
cfg.agents.defaults = cfg.agents.defaults || {};

cfg.agents.list = [
  {
    id: 'main',
    default: true,
    name: 'SpongeBot',
    workspace: '/data/workspace',
    agentDir: '/data/.openclaw/agents/main/agent',
    tools: {
      allow: ['group:sessions', 'read', 'write', 'edit', 'exec', 'process', 'message', 'memory_search', 'memory_get', 'web_search', 'web_fetch', 'browser', 'nodes', 'pdf'],
      deny: []
    }
  },
  {
    id: 'sandy',
    name: 'Sandy',
    workspace: '/data/.openclaw/workspace-sandy',
    agentDir: '/data/.openclaw/agents/sandy/agent',
    tools: {
      allow: ['group:runtime', 'group:fs', 'message', 'web_search', 'web_fetch', 'sessions_send', 'sessions_list', 'sessions_history', 'session_status'],
      deny: ['sessions_spawn']
    }
  },
  {
    id: 'glados',
    name: 'GLaDOS',
    workspace: '/data/.openclaw/workspace-glados',
    agentDir: '/data/.openclaw/agents/glados/agent',
    tools: {
      allow: ['group:runtime', 'group:fs', 'message', 'web_search', 'web_fetch', 'pdf', 'sessions_send', 'sessions_list', 'sessions_history', 'session_status'],
      deny: ['sessions_spawn']
    }
  },
  {
    id: 'squid',
    name: 'Squidward',
    workspace: '/data/.openclaw/workspace-squid',
    agentDir: '/data/.openclaw/agents/squid/agent',
    tools: {
      allow: ['group:sessions', 'group:fs', 'read', 'write', 'edit', 'memory_search', 'memory_get', 'session_status'],
      deny: ['exec', 'process', 'browser', 'nodes']
    }
  }
];

cfg.bindings = [
  { agentId: 'main', match: { channel: 'discord', accountId: 'main' } },
  { agentId: 'sandy', match: { channel: 'discord', accountId: 'sandy' } },
  { agentId: 'glados', match: { channel: 'discord', accountId: 'glados' } }
];

cfg.tools = cfg.tools || {};
cfg.tools.agentToAgent = {
  enabled: true,
  allow: ['main', 'sandy', 'glados', 'squid']
};
cfg.tools.sessions = cfg.tools.sessions || {};
cfg.tools.sessions.visibility = 'all';

cfg.session = cfg.session || {};
cfg.session.agentToAgent = cfg.session.agentToAgent || {};
cfg.session.agentToAgent.maxPingPongTurns = 2;

cfg.channels = cfg.channels || {};
cfg.channels.discord = cfg.channels.discord || {};

const discord = cfg.channels.discord;
const currentToken = discord.token;
const currentGuilds = discord.guilds || {};

discord.defaultAccount = 'main';
discord.accounts = discord.accounts || {};
discord.accounts.main = {
  ...(discord.accounts.main || {}),
  token: (discord.accounts.main && discord.accounts.main.token) || currentToken,
  guilds: (discord.accounts.main && discord.accounts.main.guilds) || currentGuilds
};
discord.accounts.sandy = {
  ...(discord.accounts.sandy || {}),
  token: sandyToken,
  guilds: (discord.accounts.sandy && discord.accounts.sandy.guilds) || currentGuilds
};
discord.accounts.glados = {
  ...(discord.accounts.glados || {}),
  token: gladosToken,
  guilds: (discord.accounts.glados && discord.accounts.glados.guilds) || currentGuilds
};

// Keep top-level discord settings; remove single-token field to avoid ambiguity
if (discord.token) delete discord.token;

fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2) + '\n', 'utf8');
console.log('Patched config:', configPath);
console.log('Backup saved:', backupPath);
console.log('Next step: openclaw gateway restart');
