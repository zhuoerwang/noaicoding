/**
 * Build script: reads ../projects/ and generates JSON data for the website.
 * - src/data/project-index.json  (lightweight manifest for landing page)
 * - public/projects/<slug>.json  (per-project data, fetched on demand)
 */
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from 'fs';
import { join, resolve } from 'path';

const ROOT = resolve(import.meta.dirname, '..', '..');
const PROJECTS_DIR = join(ROOT, 'fundamentals');
const OUT_INDEX = join(ROOT, 'website', 'src', 'data', 'project-index.json');
const OUT_PUBLIC = join(ROOT, 'website', 'public', 'projects');

// Project metadata from the root readme (order matters)
const PROJECT_META: {
  num: number;
  name: string;
  slug: string;
  dir: string;
  phase: number;
  phaseName: string;
  difficulty: string;
  concepts: string;
  pyodide: 'full' | 'partial' | 'none';
}[] = [
  // Phase 1: Data Structure Foundations
  { num: 1, name: 'KV Store', slug: 'database', dir: 'database', phase: 1, phaseName: 'Data Structure Foundations', difficulty: 'Easy', concepts: 'Hash map, TTL, persistence', pyodide: 'full' },
  { num: 2, name: 'LRU Cache', slug: 'lru', dir: 'lru', phase: 1, phaseName: 'Data Structure Foundations', difficulty: 'Easy', concepts: 'Doubly-linked list, eviction, O(1) get/put', pyodide: 'full' },
  { num: 3, name: 'Rate Limiter', slug: 'rate', dir: 'rate', phase: 1, phaseName: 'Data Structure Foundations', difficulty: 'Easy-Medium', concepts: 'Sliding window, token bucket, time-based algorithms', pyodide: 'full' },
  // Phase 2: Parsing
  { num: 4, name: 'CSV Parser', slug: 'csv_parser', dir: 'csv_parser', phase: 2, phaseName: 'Parsing', difficulty: 'Medium', concepts: 'State machine, streaming, windowed aggregation', pyodide: 'full' },
  { num: 5, name: 'JSON Parser', slug: 'json_parser', dir: 'json_parser', phase: 2, phaseName: 'Parsing', difficulty: 'Medium', concepts: 'Lexer, recursive descent, serialization', pyodide: 'full' },
  { num: 6, name: 'Regex Engine', slug: 'regex', dir: 'regex', phase: 2, phaseName: 'Parsing', difficulty: 'Medium-Hard', concepts: 'NFA, DFA, Thompson\'s construction, finite automata', pyodide: 'full' },
  // Phase 3: Networking
  { num: 7, name: 'DNS Resolver', slug: 'dns', dir: 'dns', phase: 3, phaseName: 'Networking', difficulty: 'Medium', concepts: 'UDP, packet parsing, recursive resolution, caching', pyodide: 'none' },
  { num: 8, name: 'HTTP Server', slug: 'http_server', dir: 'http_server', phase: 3, phaseName: 'Networking', difficulty: 'Medium', concepts: 'TCP sockets, request parsing, routing', pyodide: 'none' },
  { num: 9, name: 'Web Crawler', slug: 'crawler', dir: 'crawler', phase: 3, phaseName: 'Networking', difficulty: 'Medium', concepts: 'BFS, async/await, retry with backoff', pyodide: 'partial' },
  { num: 10, name: 'WebSocket', slug: 'websocket', dir: 'websocket', phase: 3, phaseName: 'Networking', difficulty: 'Medium-Hard', concepts: 'Upgrade handshake, frame protocol, connection lifecycle', pyodide: 'none' },
  // Phase 4: Core Systems
  { num: 11, name: 'Load Balancer', slug: 'load_balancer', dir: 'load_balancer', phase: 4, phaseName: 'Core Systems', difficulty: 'Medium', concepts: 'Round robin, consistent hashing, health checks, sticky sessions', pyodide: 'full' },
  { num: 12, name: 'Task Scheduler', slug: 'scheduler', dir: 'scheduler', phase: 4, phaseName: 'Core Systems', difficulty: 'Medium', concepts: 'Priority queue, async workers, retry + DLQ', pyodide: 'partial' },
  { num: 13, name: 'Pub/Sub', slug: 'pubsub', dir: 'pubsub', phase: 4, phaseName: 'Core Systems', difficulty: 'Medium', concepts: 'Message queues, patterns, delivery guarantees, backpressure', pyodide: 'full' },
  { num: 14, name: 'Spreadsheet Engine', slug: 'spreadsheet', dir: 'spreadsheet', phase: 4, phaseName: 'Core Systems', difficulty: 'Medium-Hard', concepts: 'DAG, topological sort, expression eval, cycle detection', pyodide: 'full' },
  { num: 15, name: 'Sandbox', slug: 'sandbox', dir: 'sandbox', phase: 4, phaseName: 'Core Systems', difficulty: 'Medium-Hard', concepts: 'Subprocess isolation, resource limits, virtual filesystem', pyodide: 'none' },
  // Phase 5: Dev Tools
  { num: 16, name: 'Shell', slug: 'shell', dir: 'shell', phase: 5, phaseName: 'Dev Tools', difficulty: 'Medium-Hard', concepts: 'REPL, pipes, redirection, job control, globbing', pyodide: 'none' },
  { num: 17, name: 'Git', slug: 'git', dir: 'git', phase: 5, phaseName: 'Dev Tools', difficulty: 'Hard', concepts: 'Content-addressable storage (SHA-1), commits, branches, 3-way merge', pyodide: 'full' },
  { num: 18, name: 'Compression', slug: 'compression', dir: 'compression', phase: 5, phaseName: 'Dev Tools', difficulty: 'Hard', concepts: 'Huffman coding, LZ77, DEFLATE, gzip format', pyodide: 'full' },
  // Phase 6: Advanced Systems
  { num: 19, name: 'SQL Database', slug: 'database_sql', dir: 'database_sql', phase: 6, phaseName: 'Advanced Systems', difficulty: 'Hard', concepts: 'B-tree, SQL parser, query execution, joins, optimizer', pyodide: 'full' },
  { num: 20, name: 'Compiler', slug: 'compiler', dir: 'compiler', phase: 6, phaseName: 'Advanced Systems', difficulty: 'Very Hard', concepts: 'Lexer, parser, AST, interpreter, bytecode VM, optimizations', pyodide: 'full' },
  // Phase 7: Game AI
  { num: 21, name: 'Checker Board Game', slug: 'checker', dir: 'checker', phase: 7, phaseName: 'Game AI', difficulty: 'Medium-Hard', concepts: 'Minimax, alpha-beta pruning, evaluation functions', pyodide: 'full' },
  // Phase 8: ML Foundations
  { num: 22, name: 'BPE Tokenizer', slug: 'bpe', dir: 'bpe', phase: 8, phaseName: 'ML Foundations', difficulty: 'Medium', concepts: 'Byte-pair encoding, merge rules, encode/decode', pyodide: 'full' },
  { num: 23, name: 'Autograd Engine', slug: 'autograd', dir: 'autograd', phase: 8, phaseName: 'ML Foundations', difficulty: 'Hard', concepts: 'Value class, backprop, chain rule, neuron/MLP, training', pyodide: 'full' },
  { num: 24, name: 'Transformer', slug: 'transformer', dir: 'transformer', phase: 8, phaseName: 'ML Foundations', difficulty: 'Hard', concepts: 'Embeddings, self-attention, multi-head, generation', pyodide: 'partial' },
  // Phase 9: ML Training
  { num: 25, name: 'Fine-tune + LoRA', slug: 'finetune', dir: 'finetune', phase: 9, phaseName: 'ML Training', difficulty: 'Hard', concepts: 'Data prep, full fine-tune, low-rank adapters, merge', pyodide: 'none' },
  { num: 26, name: 'RL', slug: 'rl', dir: 'rl', phase: 9, phaseName: 'ML Training', difficulty: 'Hard', concepts: 'Q-learning, REINFORCE, policy gradient, train Checker agent', pyodide: 'partial' },
  // Phase 10: AI Applications
  { num: 27, name: 'RAG', slug: 'rag', dir: 'rag', phase: 10, phaseName: 'AI Applications', difficulty: 'Medium-Hard', concepts: 'Chunking, vector store, cosine similarity, retrieval + ranking', pyodide: 'full' },
  { num: 28, name: 'AI Chatbot', slug: 'chatbot', dir: 'chatbot', phase: 10, phaseName: 'AI Applications', difficulty: 'Medium-Hard', concepts: 'Conversation, streaming tokens, tool use, context window', pyodide: 'none' },
  { num: 29, name: 'Coding Agent', slug: 'agent', dir: 'agent', phase: 10, phaseName: 'AI Applications', difficulty: 'Hard', concepts: 'Tool system, ReAct loop, coding tools, planning + error recovery', pyodide: 'none' },
  // Phase 11: Crypto
  { num: 30, name: 'Bitcoin', slug: 'bitcoin', dir: 'bitcoin', phase: 11, phaseName: 'Crypto', difficulty: 'Hard', concepts: 'SHA-256, ECDSA, transactions, Merkle tree, proof of work, blockchain', pyodide: 'full' },
];

function readFileOpt(path: string): string | null {
  try {
    return readFileSync(path, 'utf-8');
  } catch {
    return null;
  }
}

function countLevels(testContent: string): number {
  const matches = testContent.match(/class TestLevel\d+/g);
  return matches ? matches.length : 0;
}

function extractImportInfo(testContent: string): { moduleName: string; className: string } {
  // Match: from <module> import <class>
  const match = testContent.match(/^from (\w+) import (.+)$/m);
  if (match) {
    const classes = match[2].split(',').map(s => s.trim());
    return { moduleName: match[1], className: classes[0] };
  }
  return { moduleName: '', className: '' };
}

function findTestFile(dirPath: string): string | null {
  try {
    const files = readdirSync(dirPath);
    const testFile = files.find(f => f.startsWith('test_') && f.endsWith('.py'));
    return testFile ? join(dirPath, testFile) : null;
  } catch {
    return null;
  }
}

// Ensure output directories
mkdirSync(join(ROOT, 'website', 'src', 'data'), { recursive: true });
mkdirSync(OUT_PUBLIC, { recursive: true });

const index: {
  num: number;
  name: string;
  slug: string;
  phase: number;
  phaseName: string;
  difficulty: string;
  concepts: string;
  levels: number;
  pyodide: string;
  hasTests: boolean;
}[] = [];

for (const meta of PROJECT_META) {
  const dirPath = join(PROJECTS_DIR, meta.dir);
  if (!existsSync(dirPath)) {
    console.warn(`Warning: directory not found for ${meta.name}: ${dirPath}`);
    continue;
  }

  const readme = readFileOpt(join(dirPath, 'README.md'));
  const testFilePath = findTestFile(dirPath);
  const testContent = testFilePath ? readFileOpt(testFilePath) : null;
  const levels = testContent ? countLevels(testContent) : 0;
  const { moduleName, className } = testContent ? extractImportInfo(testContent) : { moduleName: '', className: '' };

  // Landing page index entry
  index.push({
    num: meta.num,
    name: meta.name,
    slug: meta.slug,
    phase: meta.phase,
    phaseName: meta.phaseName,
    difficulty: meta.difficulty,
    concepts: meta.concepts,
    levels,
    pyodide: meta.pyodide,
    hasTests: !!testContent,
  });

  // Per-project detail file
  const projectData = {
    num: meta.num,
    name: meta.name,
    slug: meta.slug,
    phase: meta.phase,
    phaseName: meta.phaseName,
    difficulty: meta.difficulty,
    concepts: meta.concepts,
    levels,
    pyodide: meta.pyodide,
    moduleName,
    className,
    hasTests: !!testContent,
    readme: readme || `# Project ${meta.num}: ${meta.name}\n\nREADME coming soon.`,
    testFile: testContent || '',
    testFileName: testFilePath ? testFilePath.split('/').pop()! : '',
  };

  writeFileSync(join(OUT_PUBLIC, `${meta.slug}.json`), JSON.stringify(projectData));
}

writeFileSync(OUT_INDEX, JSON.stringify(index, null, 2));
console.log(`Built project data: ${index.length} projects, ${index.filter(p => p.hasTests).length} with tests`);
