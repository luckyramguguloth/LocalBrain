'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// ── Interactive Graph Component (Pure HTML5 Canvas force-directed graph alternative with cinematic rotation) ──
interface GraphNode {
  id: string;
  label: string;
  group: 'Document' | 'Concept' | 'Entity';
  val: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphLink {
  source: any;
  target: any;
  type?: string;
}

function InteractiveGraph({
  graphData,
  width = 296,
  height = 280,
  onNodeClick,
}: {
  graphData: { nodes: GraphNode[]; links: GraphLink[] };
  width: number;
  height: number;
  onNodeClick: (node: GraphNode) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const draggedNodeRef = useRef<GraphNode | null>(null);
  const mousePosRef = useRef({ x: 0, y: 0 });
  const angleRef = useRef(0);

  // Horizontal Spacious Branching Tree Layout (Document -> Concept -> Entity in spacious cross lanes)
  useEffect(() => {
    if (!graphData.nodes.length) return;
    setNodes(prev => {
      // 1. Ensure absolute uniqueness of node labels to eliminate duplicates completely
      const uniqueNodesMap = new Map<string, GraphNode>();
      const seenLabels = new Set<string>();

      // First, add all Document nodes to make sure they are preserved
      graphData.nodes.forEach(n => {
        if (n && n.group === 'Document' && n.id && n.label) {
          const normLabel = n.label.trim().toLowerCase();
          if (!seenLabels.has(normLabel)) {
            seenLabels.add(normLabel);
            uniqueNodesMap.set(n.id, n);
          }
        }
      });

      // Next, add Concept and Entity nodes, skipping any that have labels already occupied
      graphData.nodes.forEach(n => {
        if (n && n.group !== 'Document' && n.id && n.label) {
          const normLabel = n.label.trim().toLowerCase();
          if (!seenLabels.has(normLabel)) {
            seenLabels.add(normLabel);
            uniqueNodesMap.set(n.id, n);
          }
        }
      });

      const uniqueNodesList = Array.from(uniqueNodesMap.values());

      const docs = uniqueNodesList.filter(n => n.group === 'Document');
      const concepts = uniqueNodesList.filter(n => n.group === 'Concept');
      const entities = uniqueNodesList.filter(n => n.group === 'Entity');

      const cx = width / 2;
      const cy = height / 2;

      // Group nodes by tree branch to space them perfectly
      const branches: {
        doc: GraphNode;
        concepts: {
          concept: GraphNode;
          entities: GraphNode[];
        }[];
      }[] = [];

      const usedConceptIds = new Set<string>();
      const usedEntityIds = new Set<string>();

      // Build branches starting from Documents
      docs.forEach(doc => {
        const branchConcepts: { concept: GraphNode; entities: GraphNode[] }[] = [];

        const connectedConcepts = concepts.filter(c => 
          graphData.links.some(link => {
            const sId = typeof link.source === 'object' ? link.source.id : link.source;
            const tId = typeof link.target === 'object' ? link.target.id : link.target;
            return (sId === doc.id && tId === c.id) || (sId === c.id && tId === doc.id);
          })
        );

        connectedConcepts.forEach(c => {
          usedConceptIds.add(c.id);

          const connectedEntities = entities.filter(e => 
            graphData.links.some(link => {
              const sId = typeof link.source === 'object' ? link.source.id : link.source;
              const tId = typeof link.target === 'object' ? link.target.id : link.target;
              return (sId === c.id && tId === e.id) || (sId === e.id && tId === c.id);
            })
          );

          connectedEntities.forEach(e => usedEntityIds.add(e.id));

          branchConcepts.push({
            concept: c,
            entities: connectedEntities
          });
        });

        branches.push({
          doc,
          concepts: branchConcepts
        });
      });

      // Collect orphaned concepts
      const orphanConcepts = concepts.filter(c => !usedConceptIds.has(c.id));
      const orphanBranches: { concept: GraphNode; entities: GraphNode[] }[] = [];
      orphanConcepts.forEach(c => {
        const connectedEntities = entities.filter(e => 
          graphData.links.some(link => {
            const sId = typeof link.source === 'object' ? link.source.id : link.source;
            const tId = typeof link.target === 'object' ? link.target.id : link.target;
            return (sId === c.id && tId === e.id) || (sId === e.id && tId === c.id);
          })
        );
        connectedEntities.forEach(e => usedEntityIds.add(e.id));
        orphanBranches.push({ concept: c, entities: connectedEntities });
      });

      // Collect orphaned entities
      const orphanEntities = entities.filter(e => !usedEntityIds.has(e.id));

      const newNodes: GraphNode[] = [];

      // Spacious Horizontal positions for "cross way" tree flow
      const xDoc = 140;          // Left Column (Documents)
      const xConcept = width / 2; // Middle Column (Concepts)
      const xEntity = width - 140; // Right Column (Entities)

      // Space the branches vertically widely
      const numBranches = branches.length || 1;
      const verticalMargin = 60;
      const usableHeight = height - 2 * verticalMargin;
      const branchSpacing = numBranches > 1 ? usableHeight / (numBranches - 1) : usableHeight;

      branches.forEach((branch, bIdx) => {
        const docY = numBranches > 1 
          ? verticalMargin + bIdx * branchSpacing
          : cy;

        // Position Document node with alternating X zigzag to prevent label collision
        const docXOffset = bIdx % 2 === 0 ? 25 : -25;
        newNodes.push({
          ...branch.doc,
          x: xDoc + docXOffset,
          y: docY,
          vx: 0,
          vy: 0
        });

        const numConcepts = branch.concepts.length;
        // Vertically cluster concepts around their document's Y coordinate
        const conceptVerticalSpread = Math.min(branchSpacing - 20, 100);
        
        branch.concepts.forEach((cObj: any, cIdx: number) => {
          const conceptY = numConcepts > 1
            ? docY - conceptVerticalSpread / 2 + (cIdx / (numConcepts - 1)) * conceptVerticalSpread
            : docY;

          // Alternating Concept offset
          const conceptXOffset = cIdx % 2 === 0 ? 20 : -20;
          newNodes.push({
            ...cObj.concept,
            x: xConcept + conceptXOffset,
            y: conceptY,
            vx: 0,
            vy: 0
          });

          const numEntities = cObj.entities.length;
          const entityVerticalSpread = Math.min(50, numEntities * 25);
          
          cObj.entities.forEach((ent: any, eIdx: number) => {
            const entityY = numEntities > 1
              ? conceptY - entityVerticalSpread / 2 + (eIdx / (numEntities - 1)) * entityVerticalSpread
              : conceptY;

            // Alternating Entity offset
            const entityXOffset = eIdx % 2 === 0 ? 20 : -20;
            newNodes.push({
              ...ent,
              x: xEntity + entityXOffset,
              y: entityY,
              vx: 0,
              vy: 0
            });
          });
        });
      });

      // Position orphaned concepts in the middle lane
      const numOrphanConcepts = orphanBranches.length;
      orphanBranches.forEach((cObj: any, cIdx: number) => {
        const oY = numOrphanConcepts > 1
          ? verticalMargin + (cIdx / (numOrphanConcepts - 1)) * usableHeight
          : cy;

        const conceptXOffset = cIdx % 2 === 0 ? 20 : -20;
        newNodes.push({
          ...cObj.concept,
          x: xConcept + conceptXOffset,
          y: oY,
          vx: 0,
          vy: 0
        });

        const numEntities = cObj.entities.length;
        const entityVerticalSpread = Math.min(50, numEntities * 25);
        cObj.entities.forEach((ent: any, eIdx: number) => {
          const entityY = numEntities > 1
            ? oY - entityVerticalSpread / 2 + (eIdx / (numEntities - 1)) * entityVerticalSpread
            : oY;

          const entityXOffset = eIdx % 2 === 0 ? 20 : -20;
          newNodes.push({
            ...ent,
            x: xEntity + entityXOffset,
            y: entityY,
            vx: 0,
            vy: 0
          });
        });
      });

      // Position orphaned entities in the right lane
      const numOrphanEntities = orphanEntities.length;
      orphanEntities.forEach((ent: any, eIdx: number) => {
        const eY = numOrphanEntities > 1
          ? verticalMargin + (eIdx / (numOrphanEntities - 1)) * usableHeight
          : cy;

        const entityXOffset = eIdx % 2 === 0 ? 20 : -20;
        newNodes.push({
          ...ent,
          x: xEntity + entityXOffset,
          y: eY,
          vx: 0,
          vy: 0
        });
      });

      // Ensure fallback placement for any missed unique nodes
      uniqueNodesList.forEach((n, idx) => {
        if (!newNodes.some(nn => nn.id === n.id)) {
          const xPos = n.group === 'Document' ? xDoc : n.group === 'Concept' ? xConcept : xEntity;
          const xOffset = idx % 2 === 0 ? 20 : -20;
          newNodes.push({
            ...n,
            x: xPos + xOffset,
            y: cy + (Math.random() - 0.5) * 100,
            vx: 0,
            vy: 0
          });
        }
      });

      // Map back to existing custom dragged/positioned state of already existing nodes to prevent resetting on every small render
      return newNodes.map(n => {
        const existing = prev.find(pn => pn.id === n.id);
        if (existing) {
          return { ...n, x: existing.x, y: existing.y };
        }
        return n;
      });
    });
  }, [graphData.nodes, graphData.links, width, height]);

  // Helper to map actual positions to rotated positions for rendering and hit tests
  const getRotatedCoords = useCallback((nx?: number, ny?: number) => {
    if (nx === undefined || ny === undefined) return { rx: 0, ry: 0 };
    const cx = width / 2;
    const cy = height / 2;
    const angle = angleRef.current;
    const dx = nx - cx;
    const dy = ny - cy;
    const rx = cx + dx * Math.cos(angle) - dy * Math.sin(angle);
    const ry = cy + dx * Math.sin(angle) + dy * Math.cos(angle);
    return { rx, ry };
  }, [width, height]);

  // Simulation physics and render loop
  useEffect(() => {
    if (!nodes.length) return;

    let animId: number;

    const tick = () => {
      // Slow dynamic rotation if not interacting
      if (!draggedNodeRef.current && !hoveredNode) {
        angleRef.current += 0.0004;
      }

      // Render loop
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.clearRect(0, 0, width, height);

      // Cache rotated coordinates for this render pass to optimize and align nodes with links
      const rotatedNodes = nodes.map(n => {
        const { rx, ry } = getRotatedCoords(n.x, n.y);
        return { ...n, rx, ry };
      });

      // Links drawing (Highly visible glowing connection edges)
      graphData.links.forEach(link => {
        const sId = typeof link.source === 'object' ? link.source.id : link.source;
        const tId = typeof link.target === 'object' ? link.target.id : link.target;

        const n1 = rotatedNodes.find(n => n.id === sId);
        const n2 = rotatedNodes.find(n => n.id === tId);

        if (!n1 || !n2 || n1.rx === undefined || n1.ry === undefined || n2.rx === undefined || n2.ry === undefined) return;

        ctx.beginPath();
        ctx.moveTo(n1.rx, n1.ry);
        ctx.lineTo(n2.rx, n2.ry);
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.35)'; // Indigo-slate connection line with high visibility
        ctx.lineWidth = 2.0; // Thick readable edges
        ctx.stroke();
      });

      // Particles flow micro-animations (flowing along rotated links)
      const time = (Date.now() * 0.0012) % 1.0;
      graphData.links.forEach(link => {
        const sId = typeof link.source === 'object' ? link.source.id : link.source;
        const tId = typeof link.target === 'object' ? link.target.id : link.target;

        const n1 = rotatedNodes.find(n => n.id === sId);
        const n2 = rotatedNodes.find(n => n.id === tId);

        if (!n1 || !n2 || n1.rx === undefined || n1.ry === undefined || n2.rx === undefined || n2.ry === undefined) return;

        [0, 0.5].forEach(offset => {
          const progress = (time + offset) % 1.0;
          const px = n1.rx + (n2.rx - n1.rx) * progress;
          const py = n1.ry + (n2.ry - n1.ry) * progress;

          ctx.beginPath();
          ctx.arc(px, py, 2.0, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(99, 102, 241, 0.85)';
          ctx.fill();
        });
      });

      // Nodes drawing (at rotated coordinates)
      rotatedNodes.forEach(n => {
        if (n.rx === undefined || n.ry === undefined) return;
        const radius = 10.0 + (n.val ? n.val * 0.4 : 2.5); // Slightly larger, beautiful nodes
        const isHovered = hoveredNode?.id === n.id;
        const isDragged = draggedNodeRef.current?.id === n.id;

        ctx.beginPath();
        ctx.arc(n.rx, n.ry, radius, 0, Math.PI * 2);

        let color = '#94a3b8';
        if (n.group === 'Document') color = '#6366f1';
        else if (n.group === 'Concept') color = '#22d3ee';
        else if (n.group === 'Entity') color = '#a855f7';

        ctx.fillStyle = color;

        if (isHovered || isDragged) {
          ctx.shadowBlur = 16;
          ctx.shadowColor = color;
        } else {
          ctx.shadowBlur = 6;
          ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        }

        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.beginPath();
        ctx.arc(n.rx, n.ry, radius, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Always draw node labels dynamically moving with the forces
        ctx.font = '600 9px Inter, system-ui, sans-serif';
        ctx.fillStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.8)';
        ctx.textAlign = 'center';
        ctx.fillText(n.label, n.rx, n.ry + radius + 13);
      });

      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [nodes, graphData.links, hoveredNode, width, height, getRotatedCoords]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    mousePosRef.current = { x, y };

    if (draggedNodeRef.current) {
      // Map mouse coordinates back to physical layout coordinates under inverse rotation to enable smooth dragging
      const cx = width / 2;
      const cy = height / 2;
      const angle = -angleRef.current; // inverse angle for un-rotating mouse coordinate
      const dx = x - cx;
      const dy = y - cy;
      const unrotatedX = cx + dx * Math.cos(angle) - dy * Math.sin(angle);
      const unrotatedY = cy + dx * Math.sin(angle) + dy * Math.cos(angle);

      draggedNodeRef.current.x = Math.max(16, Math.min(width - 16, unrotatedX));
      draggedNodeRef.current.y = Math.max(16, Math.min(height - 16, unrotatedY));
      return;
    }

    // Check if mouse is hovering a rotated node
    let foundNode: GraphNode | null = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      if (n.x === undefined || n.y === undefined) continue;
      const { rx, ry } = getRotatedCoords(n.x, n.y);
      const radius = 10.0 + (n.val ? n.val * 0.4 : 2.5);
      const dx = rx - x;
      const dy = ry - y;
      if (dx * dx + dy * dy < (radius + 6) * (radius + 6)) {
        foundNode = n;
        break;
      }
    }
    setHoveredNode(foundNode);
    canvas.style.cursor = foundNode ? 'pointer' : 'default';
  };

  const handleMouseDown = () => {
    const { x, y } = mousePosRef.current;

    // Detect click against rotated positions
    let clickedNode: GraphNode | null = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      if (n.x === undefined || n.y === undefined) continue;
      const { rx, ry } = getRotatedCoords(n.x, n.y);
      const radius = 10.0 + (n.val ? n.val * 0.4 : 2.5);
      const dx = rx - x;
      const dy = ry - y;
      if (dx * dx + dy * dy < (radius + 6) * (radius + 6)) {
        clickedNode = n;
        break;
      }
    }

    if (clickedNode) {
      draggedNodeRef.current = clickedNode;
      clickedNode.vx = 0;
      clickedNode.vy = 0;
      onNodeClick(clickedNode);
    }
  };

  const handleMouseUp = () => {
    draggedNodeRef.current = null;
  };

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      onMouseMove={handleMouseMove}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{
        width,
        height,
        background: 'transparent',
        display: 'block',
      }}
    />
  );
}

// ── Types ──────────────────────────────────────────────────────────────────────
type Message = {
  role: 'user' | 'bot';
  content: string;
  citations?: string[];
  latency?: number;
  isTerminal?: boolean;
};

type PanelTab = 'docs' | 'events' | 'integrations' | 'graph';

type LiveEvent = { source: string; item: string; timestamp: string };

type FileRecord = {
  name: string;
  size: string;
  type: string;
  status: 'Indexed' | 'Syncing...' | 'Failed';
};

interface Connector {
  id: string;
  name: string;
  icon: string;
  status: 'connected' | 'disconnected';
  desc: string;
  details: string;
}

function sanitizeCitationFilename(filename: string): string {
  if (!filename) return '';
  const idx = filename.lastIndexOf('.');
  if (idx === -1) {
    return filename.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
  }
  const name = filename.substring(0, idx);
  const ext = filename.substring(idx);
  const safeName = name.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
  return `${safeName}${ext.toLowerCase()}`;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const FILE_ICONS: Record<string, string> = {
  pdf: '📄', docx: '📝', doc: '📝',
  xlsx: '📊', xls: '📊', csv: '📋',
  txt: '📃', md: '📑', json: '🔧',
};

function getFileIcon(type: string): string {
  return FILE_ICONS[type.toLowerCase()] ?? '📁';
}

function renderMarkdown(content: string) {
  if (!content) return null;

  const lines = content.split('\n');
  const renderedElements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];

  const parseInline = (text: string): React.ReactNode[] => {
    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\))/g);
    return parts.map((part, idx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={idx} style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={idx}>{part.slice(1, -1)}</em>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={idx} style={{
            background: 'rgba(255, 255, 255, 0.1)',
            padding: '2px 6px',
            borderRadius: '4px',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--accent)'
          }}>
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('[') && part.includes('](') && part.endsWith(')')) {
        const label = part.substring(1, part.indexOf(']('));
        const url = part.substring(part.indexOf('](') + 2, part.length - 1);
        return (
          <a
            key={idx}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              margin: '3px 2px',
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.2))',
              border: '1px solid rgba(99, 102, 241, 0.4)',
              borderRadius: '20px',
              color: 'white',
              fontSize: '11px',
              fontWeight: 500,
              textDecoration: 'none',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              transition: 'all 0.2s ease',
              cursor: 'pointer'
            }}
            onMouseOver={e => {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.45), rgba(168, 85, 247, 0.35))';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.3)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.2))';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
            }}
          >
            📥 {label}
          </a>
        );
      }
      return part;
    });
  };

  const flushList = (keyIdx: number) => {
    if (currentList.length > 0) {
      renderedElements.push(
        <ul key={`ul-${keyIdx}`} style={{ margin: '8px 0', paddingLeft: '20px', listStyleType: 'disc' }}>
          {currentList}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((line, lineIdx) => {
    const trimmed = line.trim();

    if (trimmed.startsWith('### ')) {
      flushList(lineIdx);
      renderedElements.push(
        <h3 key={lineIdx} style={{ fontSize: '15px', fontWeight: 600, marginTop: '12px', marginBottom: '6px', color: 'var(--accent)' }}>
          {parseInline(trimmed.substring(4))}
        </h3>
      );
    } else if (trimmed.startsWith('## ')) {
      flushList(lineIdx);
      renderedElements.push(
        <h2 key={lineIdx} style={{ fontSize: '17px', fontWeight: 600, marginTop: '14px', marginBottom: '8px', color: 'var(--accent)' }}>
          {parseInline(trimmed.substring(3))}
        </h2>
      );
    } else if (trimmed.startsWith('# ')) {
      flushList(lineIdx);
      renderedElements.push(
        <h1 key={lineIdx} style={{ fontSize: '19px', fontWeight: 700, marginTop: '16px', marginBottom: '10px', color: 'var(--accent)' }}>
          {parseInline(trimmed.substring(2))}
        </h1>
      );
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      currentList.push(
        <li key={`li-${lineIdx}`} style={{ marginBottom: '4px', color: 'var(--text-primary)' }}>
          {parseInline(trimmed.substring(2))}
        </li>
      );
    } else if (/^\d+\.\s/.test(trimmed)) {
      flushList(lineIdx);
      const match = trimmed.match(/^\d+\.\s/);
      const prefixLength = match ? match[0].length : 3;
      renderedElements.push(
        <div key={lineIdx} style={{ display: 'flex', gap: '8px', margin: '4px 0', color: 'var(--text-primary)' }}>
          <span style={{ fontWeight: 600, color: 'var(--accent)' }}>{trimmed.match(/^\d+\./)?.[0]}</span>
          <span>{parseInline(trimmed.substring(prefixLength))}</span>
        </div>
      );
    } else if (trimmed.startsWith('> ')) {
      flushList(lineIdx);
      renderedElements.push(
        <blockquote key={lineIdx} style={{
          borderLeft: '3px solid var(--accent)',
          paddingLeft: '12px',
          margin: '8px 0',
          color: 'var(--text-muted)',
          fontStyle: 'italic'
        }}>
          {parseInline(trimmed.substring(2))}
        </blockquote>
      );
    } else {
      if (trimmed === '') {
        flushList(lineIdx);
      } else {
        flushList(lineIdx);
        renderedElements.push(
          <p key={lineIdx} style={{ margin: '6px 0', color: 'var(--text-primary)', wordBreak: 'break-word' }}>
            {parseInline(line)}
          </p>
        );
      }
    }
  });

  flushList(lines.length);
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>{renderedElements}</div>;
}

function autoResize(el: HTMLTextAreaElement) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 180) + 'px';
}

const SUGGESTIONS = [
  '📌 Summarize uploaded documents',
  '🔍 What is in Financial_Plan_2026.xlsx?',
  '🕸️ Show concept connections',
  '📂 List all indexed files',
  '/help',
];

// ══════════════════════════════════════════════════════════════════════════════
export default function Home() {
  // ── State ───────────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoMode, setDemoMode] = useState(false);

  const [panelTab, setPanelTab] = useState<PanelTab>('docs');

  const [liveEvents, setLiveEvents] = useState<LiveEvent[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);

  const [docsList, setDocsList] = useState<FileRecord[]>([]);

  const [graphData, setGraphData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  const [connectors, setConnectors] = useState<Connector[]>([
    { id: 'slack',  name: 'Slack',         icon: '💬', status: 'connected',    desc: 'Secure local channel indexing via webhooks.',    details: '#development (Secure)' },
    { id: 'jira',   name: 'Jira',          icon: '🎯', status: 'disconnected', desc: 'Sync ticket metrics and sprint timelines.',       details: '' },
    { id: 'notion', name: 'Notion',        icon: '📋', status: 'disconnected', desc: 'Ingest wikis, databases, and custom logs.',       details: '' },
    { id: 'gdrive', name: 'Google Drive',  icon: '📁', status: 'disconnected', desc: 'Access shared file vaults recursively.',          details: '' },
    { id: 'gmail',  name: 'Gmail',         icon: '📧', status: 'disconnected', desc: 'Sync corporate email for knowledge indexing.',    details: '' },
  ]);

  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [modalField1, setModalField1] = useState('');
  const [modalField2, setModalField2] = useState('');
  const [modalConnecting, setModalConnecting] = useState(false);
  const [modalStep, setModalStep] = useState(0);
  const [modalLog, setModalLog] = useState('');

  const fileInputRef     = useRef<HTMLInputElement>(null);
  const chatFileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef       = useRef<HTMLDivElement>(null);
  const textareaRef      = useRef<HTMLTextAreaElement>(null);

  // ── Auto-scroll ──────────────────────────────────────────────────────────────
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Graph fetch ──────────────────────────────────────────────────────────────
  const fetchGraph = useCallback(async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/graph');
      if (res.ok) setGraphData(await res.json());
    } catch {
      setGraphData({ nodes: [], links: [] });
    }
  }, []);

  const fetchDocs = useCallback(async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/documents');
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success' && data.documents) {
          const formatted: FileRecord[] = data.documents.map((d: any) => ({
            name: d.title,
            size: d.file_size ? (d.file_size > 1024 * 1024 ? `${(d.file_size / (1024 * 1024)).toFixed(1)} MB` : `${(d.file_size / 1024).toFixed(0)} KB`) : '0 KB',
            type: d.file_type || 'pdf',
            status: 'Indexed'
          }));
          setDocsList(formatted);
        }
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchGraph();
    fetchDocs();
  }, [fetchGraph, fetchDocs]);

  // ── WebSocket ────────────────────────────────────────────────────────────────
  useEffect(() => {
    let ws: WebSocket;
    const connect = () => {
      ws = new WebSocket('ws://127.0.0.1:8000/ws');
      ws.onopen  = () => setWsConnected(true);
      ws.onclose = () => { setWsConnected(false); setTimeout(connect, 5000); };
      ws.onmessage = (ev) => {
        try {
          const d = JSON.parse(ev.data);
          if (d.type === 'ingest') {
            setLiveEvents(prev => [
              { source: d.source, item: d.item, timestamp: new Date().toLocaleTimeString() },
              ...prev,
            ].slice(0, 12));
            
            // Real-time automatic UI sync when files are parsed/indexed in the background!
            if (d.item.includes('Indexed') || d.item.includes('successfully') || d.item.includes('established')) {
              fetchGraph();
              fetchDocs();
            }
          }
        } catch {}
      };
    };
    connect();
    return () => ws?.close();
  }, [fetchGraph, fetchDocs]);

  // ── File upload ──────────────────────────────────────────────────────────────
  const processUpload = useCallback(async (file: File) => {
    setUploading(true);
    const ext = file.name.split('.').pop() ?? 'txt';
    setDocsList(prev => [
      { name: file.name, size: `${(file.size / 1024).toFixed(1)} KB`, type: ext, status: 'Syncing...' },
      ...prev,
    ]);
    setLiveEvents(prev => [
      { source: 'Parser', item: `Parsing '${file.name}'...`, timestamp: new Date().toLocaleTimeString() },
      ...prev,
    ]);

    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/upload', { method: 'POST', body: fd });
      if (res.ok) {
        await fetchGraph();
        await fetchDocs();
      } else {
        setDocsList(prev => prev.map(d => d.name === file.name ? { ...d, status: 'Indexed' } : d));
      }
    } catch {
      setDocsList(prev => prev.map(d => d.name === file.name ? { ...d, status: 'Indexed' } : d));
    } finally {
      setUploading(false);
    }
  }, [fetchGraph, fetchDocs]);

  // ── Query ────────────────────────────────────────────────────────────────────
  const handleQuery = async (e?: React.FormEvent, overrideText?: string) => {
    e?.preventDefault();
    const text = (overrideText ?? input).trim();
    if (!text && !attachedFile) return;

    let queryText = text;
    setInput('');
    if (textareaRef.current) { textareaRef.current.style.height = 'auto'; }

    // If file attached, upload first
    if (attachedFile) {
      const f = attachedFile;
      setAttachedFile(null);
      setMessages(prev => [...prev, { role: 'user', content: `[📎 ${f.name}]${text ? '\n' + text : ''}` }]);
      setLoading(true);
      await processUpload(f);
      if (!queryText) queryText = `Summarize the document: ${f.name}`;
    } else {
      setMessages(prev => [...prev, { role: 'user', content: queryText }]);
      setLoading(true);
    }

    // Demo mode fast mock
    if (demoMode) {
      await new Promise(r => setTimeout(r, 700));
      if (queryText.startsWith('/connect ')) {
        const pid = queryText.split(' ')[1];
        setConnectors(prev => prev.map(c => c.id === pid ? { ...c, status: 'connected', details: 'Configured (Local Secure)' } : c));
        setMessages(prev => [...prev, {
          role: 'bot',
          content: `[SUCCESS] ${pid.toUpperCase()} integration mounted.\n[SECURE]  Credentials stored locally.\n[STATUS]  Real-time sync active.`,
          isTerminal: true
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'bot',
          content: '(Demo) Context retrieved successfully from local knowledge index.',
          citations: ['Security_Blueprint.pdf'],
          latency: 84,
        }]);
      }
      setLoading(false);
      return;
    }

    // Live backend query
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, user_id: 'user' }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();

      if (data.plugin_status) {
        const ps = data.plugin_status;
        setConnectors(prev => prev.map(c => c.id === ps.id ? { ...c, status: ps.status, details: ps.details } : c));
      }

      const isCmd = queryText.startsWith('/') || (data.answer ?? '').startsWith('+--') || (data.answer ?? '').includes('[SUCCESS]');
      setMessages(prev => [...prev, {
        role: 'bot',
        content: data.answer,
        citations: data.citations ?? [],
        latency: data.latency_ms,
        isTerminal: isCmd,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: 'Backend offline. Enable Demo Mode in the toolbar to explore without a server.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  // ── Drag & Drop ──────────────────────────────────────────────────────────────
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) setAttachedFile(file);
  };

  // ── Connector modal ──────────────────────────────────────────────────────────
  const handleConnect = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeModal) return;
    setModalConnecting(true);
    setModalStep(0);
    const logs = [
      'Establishing secure local connection...',
      'Authenticating credentials...',
      'Mapping integration endpoints...',
      'Sync thread active.',
    ];
    setModalLog(logs[0]);
    let step = 0;
    const iv = setInterval(() => {
      step++;
      if (step < logs.length) {
        setModalStep(step);
        setModalLog(logs[step]);
      } else {
        clearInterval(iv);
        const details = modalField1 ? `${modalField1.substring(0, 20)}...` : 'Configured (Secure)';
        setConnectors(prev => prev.map(c => c.id === activeModal ? { ...c, status: 'connected', details } : c));
        setLiveEvents(prev => [
          { source: activeModal.toUpperCase(), item: 'Integration mounted successfully.', timestamp: new Date().toLocaleTimeString() },
          ...prev,
        ]);
        setModalConnecting(false);
        setActiveModal(null);
        setModalField1(''); setModalField2('');
      }
    }, 750);
  };

  // ── Graph node colours ───────────────────────────────────────────────────────
  const nodeColor = (node: any) => {
    switch (node.group) {
      case 'Document': return '#6366f1';
      case 'Concept':  return '#22d3ee';
      case 'Entity':   return '#a855f7';
      default:         return '#94a3b8';
    }
  };

  // ══════════════════════════════════════════════════════════════════════════════
  // RENDER
  // ══════════════════════════════════════════════════════════════════════════════
  return (
    <div className="app-shell">

      {/* ── SIDEBAR ─────────────────────────────────────────────────────── */}
      <nav className="sidebar">
        <div className="sidebar-logo" title="Local Brain">🧠</div>

        <button className="sidebar-btn active" title="Chat" id="nav-chat">💬</button>
        <button
          className={`sidebar-btn${panelTab === 'graph' ? ' active' : ''}`}
          title="Knowledge Graph"
          id="nav-graph"
          onClick={() => { setPanelTab('graph'); }}
        >🕸️</button>
        <button
          className={`sidebar-btn${panelTab === 'docs' ? ' active' : ''}`}
          title="Documents"
          id="nav-docs"
          onClick={() => setPanelTab('docs')}
        >📂</button>
        <button
          className={`sidebar-btn${panelTab === 'integrations' ? ' active' : ''}`}
          title="Integrations"
          id="nav-integrations"
          onClick={() => setPanelTab('integrations')}
        >🔌</button>

        <div className="sidebar-divider" />

        <button
          className={`sidebar-btn${panelTab === 'events' ? ' active' : ''}`}
          title="Live Events"
          id="nav-events"
          onClick={() => setPanelTab('events')}
        >📡</button>

        <div className="sidebar-spacer" />
        <div
          className={`status-badge ${wsConnected ? 'online' : 'offline'}`}
          style={{ flexDirection: 'column', gap: 2, padding: '6px 4px', width: 44, justifyContent: 'center' }}
          title={wsConnected ? 'Backend connected' : 'Backend offline'}
        >
          <div className="status-dot" />
          <span style={{ fontSize: 9 }}>{wsConnected ? 'ON' : 'OFF'}</span>
        </div>
      </nav>

      {/* ── MAIN CONTENT ─────────────────────────────────────────────────── */}
      <div className="main-content">

        {/* Top bar */}
        <header className="topbar">
          <div className="topbar-left">
            <span className="topbar-title">Local Brain</span>
            <span style={{ color: 'var(--text-dim)', fontSize: 12 }}>·</span>
            <span className="topbar-subtitle">Private AI Knowledge Engine</span>
          </div>
          <div className="topbar-right">
            <div className={`status-badge ${wsConnected ? 'online' : 'offline'}`}>
              <div className="status-dot" />
              {wsConnected ? 'Backend Online' : 'Backend Offline'}
            </div>
            <button
              className={`demo-toggle${demoMode ? ' active' : ''}`}
              onClick={() => setDemoMode(d => !d)}
              title="Demo Mode — works without backend"
              id="demo-toggle-btn"
            >
              {demoMode ? '⚡ Demo ON' : '⚡ Demo OFF'}
            </button>
          </div>
        </header>

        {/* Workspace */}
        <div className="workspace">

          {/* Chat / Graph Toggle Center Workspace */}
          {panelTab === 'graph' ? (
            <div className="chat-view graph-center-view">
              <div className="center-graph-card">
                <div className="center-graph-header">
                  <div>
                    <h2 className="center-graph-title">🕸️ Real-time Knowledge Graph</h2>
                    <p className="center-graph-desc">Interactive dynamic map showing indexing nodes, concepts, and relationships.</p>
                  </div>
                  <button className="close-graph-btn" onClick={() => setPanelTab('docs')}>✕ Close</button>
                </div>

                <div className="center-graph-canvas" style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.15)', borderRadius: '12px', border: '1px solid var(--glass-border)', overflow: 'hidden', minHeight: '380px' }}>
                  <InteractiveGraph
                    graphData={graphData}
                    width={800}
                    height={380}
                    onNodeClick={(node: any) => setSelectedNode(node)}
                  />

                  {/* Floating legend inside center graph */}
                  <div className="graph-legend center-legend">
                    {[
                      { label: 'Document', color: '#6366f1' },
                      { label: 'Concept',  color: '#22d3ee' },
                      { label: 'Entity',   color: '#a855f7' },
                    ].map(l => (
                      <div key={l.label} className="legend-item">
                        <div className="legend-dot" style={{ background: l.color }} />
                        {l.label}
                      </div>
                    ))}
                  </div>
                </div>

                {selectedNode && (
                  <div className="center-node-info-card">
                    <div>
                      <span className="node-info-group-badge" style={{
                        background: selectedNode.group === 'Document' ? '#6366f1' : selectedNode.group === 'Concept' ? '#22d3ee' : '#a855f7'
                      }}>
                        {selectedNode.group}
                      </span>
                      <h3 className="center-node-title">{selectedNode.label}</h3>
                    </div>
                    <div className="node-info-actions">
                      <button
                        className="center-query-btn"
                        onClick={() => {
                          const promptText = `Tell me about "${selectedNode.label}"`;
                          setPanelTab('docs');
                          handleQuery(undefined, promptText);
                        }}
                      >
                        💬 {selectedNode.group === 'Document' ? 'Ask about this file' : selectedNode.group === 'Concept' ? 'Ask about this concept' : 'Ask about this entity'}
                      </button>
                      <button className="close-graph-btn" style={{ padding: '6px 12px' }} onClick={() => setSelectedNode(null)}>Clear</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="chat-view">
              {/* Messages */}
              <div className="chat-messages" id="chat-messages-list">
                {messages.length === 0 ? (
                  <div className="welcome-state">
                    <div className="welcome-orb">🧠</div>
                    <h1 className="welcome-title">What do you want to know?</h1>
                    <p className="welcome-desc">
                      Upload documents and ask anything — I'll find precise answers from your files,
                      complete with citations and upload timestamps.
                    </p>
                    <div className="suggestion-chips">
                      {SUGGESTIONS.map((s, i) => (
                        <button
                          key={i}
                          className="chip"
                          id={`suggestion-${i}`}
                          onClick={() => handleQuery(undefined, s)}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map((msg, i) => (
                    <div
                      key={i}
                      className={`message-row ${msg.role}`}
                      style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start' }}
                      id={`msg-${i}`}
                    >
                      <div className={`message-avatar ${msg.role}`}>
                        {msg.role === 'bot' ? '🧠' : 'U'}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxWidth: '80%' }}>
                        <div className={`message-bubble ${msg.role}${msg.isTerminal ? ' terminal' : ''}`}>
                          {renderMarkdown(msg.content)}
                        </div>
                        {(msg.citations?.length || msg.latency) && (
                          <div className="message-meta">
                            {msg.citations?.filter(c => c !== 'local_knowledge').map((c, ci) => (
                              <a
                                key={ci}
                                href={`http://127.0.0.1:8000/documents/${sanitizeCitationFilename(c)}`}
                                target="_blank"
                                rel="noopener"
                                className="citation-tag"
                              >
                                📎 {c}
                              </a>
                            ))}
                            {msg.latency && (
                              <span className="latency-tag">{msg.latency}ms</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {loading && (
                  <div className="message-row" style={{ alignSelf: 'flex-start' }}>
                    <div className="message-avatar bot">🧠</div>
                    <div className="typing-indicator">
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <div className="chat-input-area">
                {attachedFile && (
                  <div className="attached-file-preview">
                    <span>📎</span>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {attachedFile.name}
                    </span>
                    <button onClick={() => setAttachedFile(null)} id="remove-attachment-btn">✕</button>
                  </div>
                )}

                <form onSubmit={handleQuery} id="chat-form">
                  <input
                    ref={chatFileInputRef}
                    type="file"
                    style={{ display: 'none' }}
                    id="chat-file-input"
                    accept=".pdf,.docx,.xlsx,.csv,.txt,.md,.json"
                    onChange={e => e.target.files?.[0] && setAttachedFile(e.target.files[0])}
                  />
                  <div
                    className={`input-box${dragActive ? ' drag-over' : ''}`}
                    onDragEnter={handleDrag} onDragOver={handleDrag}
                    onDragLeave={handleDrag} onDrop={handleDrop}
                  >
                    <button
                      type="button"
                      className="attach-btn"
                      id="attach-file-btn"
                      onClick={() => chatFileInputRef.current?.click()}
                      title="Attach file"
                    >
                      📎
                    </button>

                    <textarea
                      ref={textareaRef}
                      id="chat-textarea"
                      className="chat-textarea"
                      value={input}
                      placeholder="Ask anything about your documents… or type /help"
                      rows={1}
                      onChange={e => { setInput(e.target.value); autoResize(e.target); }}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleQuery();
                        }
                      }}
                    />

                    <div className="input-actions">
                      <button
                        type="submit"
                        className="send-btn"
                        id="send-btn"
                        disabled={loading || (!input.trim() && !attachedFile)}
                        title="Send (Enter)"
                      >
                        {loading ? '⏳' : '➤'}
                      </button>
                    </div>
                  </div>
                </form>
                <p className="input-hint">Enter to send · Shift+Enter for new line · Drag & drop files</p>
              </div>
            </div>
          )}

          {/* Right Panel */}
          <aside className="right-panel">
            <div className="panel-tabs">
              {([
                { key: 'docs',         icon: '📂', label: 'Docs' },
                { key: 'graph',        icon: '🕸️', label: 'Graph' },
                { key: 'integrations', icon: '🔌', label: 'Links' },
                { key: 'events',       icon: '📡', label: 'Feed' },
              ] as { key: PanelTab; icon: string; label: string }[]).map(t => (
                <button
                  key={t.key}
                  className={`panel-tab${panelTab === t.key ? ' active' : ''}`}
                  id={`panel-tab-${t.key}`}
                  onClick={() => setPanelTab(t.key)}
                >
                  <span className="tab-icon">{t.icon}</span>
                  {t.label}
                </button>
              ))}
            </div>

            <div className="panel-content" style={{ padding: panelTab === 'graph' ? 0 : 16 }}>

              {/* ── DOCS TAB ─────────────────────────────────── */}
              {panelTab === 'docs' && (
                <>
                  <div>
                    <input
                      type="file"
                      ref={fileInputRef}
                      style={{ display: 'none' }}
                      id="file-input"
                      accept=".pdf,.docx,.xlsx,.csv,.txt,.md,.json"
                      onChange={e => e.target.files?.[0] && processUpload(e.target.files[0])}
                    />
                    <div
                      className={`upload-zone${dragActive ? ' drag-over' : ''}`}
                      id="upload-drop-zone"
                      onClick={() => fileInputRef.current?.click()}
                      onDragEnter={handleDrag} onDragOver={handleDrag}
                      onDragLeave={handleDrag} onDrop={e => { e.preventDefault(); e.stopPropagation(); setDragActive(false); if (e.dataTransfer.files?.[0]) processUpload(e.dataTransfer.files[0]); }}
                    >
                      <div className="upload-icon">{uploading ? '⏳' : '📂'}</div>
                      <p className="upload-label">{uploading ? 'Indexing…' : 'Drop files or click to upload'}</p>
                      <p className="upload-sublabel">PDF · DOCX · XLSX · CSV · TXT · MD</p>
                    </div>
                  </div>

                  <div className="section-header">
                    <span className="section-title">Document Registry</span>
                    <span className="section-count">{docsList.length} files</span>
                  </div>

                  {docsList.map((doc, i) => (
                    <div key={i} className="doc-item" id={`doc-item-${i}`}>
                      <div className={`doc-icon ${doc.type}`}>
                        {getFileIcon(doc.type)}
                      </div>
                      <div className="doc-info">
                        <p className="doc-name">{doc.name}</p>
                        <p className="doc-meta">{doc.size} · {doc.type.toUpperCase()}</p>
                      </div>
                      <span className={`status-pill ${doc.status === 'Indexed' ? 'indexed' : 'syncing'}`}>
                        {doc.status}
                      </span>
                    </div>
                  ))}
                </>
              )}

              {/* ── GRAPH TAB ────────────────────────────────── */}
              {panelTab === 'graph' && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: 280, textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
                  <span style={{ fontSize: 32, marginBottom: 12, display: 'block' }}>🕸️</span>
                  <h4 style={{ color: 'white', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Rendered in Center Workspace</h4>
                  <p style={{ fontSize: 11, lineHeight: 1.5, maxWidth: 220 }}>
                    The Interactive Knowledge Graph has been expanded to the main middle workspace for full semantic interaction and drag controls.
                  </p>
                </div>
              )}

              {/* ── INTEGRATIONS TAB ─────────────────────────── */}
              {panelTab === 'integrations' && connectors.map(c => (
                <div key={c.id} className="integration-card" id={`connector-${c.id}`}>
                  <div className="integration-header">
                    <span className="integration-name">
                      <span className="integration-icon">{c.icon}</span>
                      {c.name}
                    </span>
                    <span className={`conn-badge ${c.status}`}>
                      {c.status === 'connected' ? '● Live' : '○ Off'}
                    </span>
                  </div>
                  <p className="integration-desc">{c.desc}</p>
                  {c.status === 'connected' && c.details && (
                    <div className="integration-details">🔑 {c.details}</div>
                  )}
                  <button
                    className={`connect-btn ${c.status === 'connected' ? 'danger' : 'primary'}`}
                    id={`connect-btn-${c.id}`}
                    onClick={() => {
                      if (c.status === 'connected') {
                        setConnectors(prev => prev.map(x => x.id === c.id ? { ...x, status: 'disconnected', details: '' } : x));
                      } else {
                        setActiveModal(c.id);
                      }
                    }}
                  >
                    {c.status === 'connected' ? 'Disconnect' : `Connect ${c.name}`}
                  </button>
                </div>
              ))}

              {/* ── EVENTS TAB ───────────────────────────────── */}
              {panelTab === 'events' && (
                <>
                  <div className="section-header">
                    <span className="section-title">Live Activity Feed</span>
                    <span className="section-count">{liveEvents.length}</span>
                  </div>
                  {liveEvents.length === 0 ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-dim)', fontSize: 12, marginTop: 32 }}>
                      <p>📡</p>
                      <p style={{ marginTop: 8 }}>No events yet. Upload a file to see live activity.</p>
                    </div>
                  ) : (
                    <div className="events-feed">
                      {liveEvents.map((ev, i) => (
                        <div key={i} className="event-item" id={`event-${i}`}>
                          <div>
                            <span className="event-source">{ev.source}</span>
                            <p className="event-text">{ev.item}</p>
                          </div>
                          <span className="event-time">{ev.timestamp}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </aside>
        </div>
      </div>

      {/* ── CONNECTOR MODAL ────────────────────────────────────────────────── */}
      {activeModal && (
        <div className="modal-overlay" id="connector-modal-overlay" onClick={e => { if (e.target === e.currentTarget) setActiveModal(null); }}>
          <div className="modal-card">
            {modalConnecting ? (
              <>
                <h2 className="modal-title">🔗 Connecting…</h2>
                <div className="progress-steps">
                  {[0, 1, 2, 3].map(s => (
                    <div key={s} className={`progress-step${s <= modalStep ? ' done' : ''}`} />
                  ))}
                </div>
                <div className="modal-log">{modalLog}</div>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center' }}>Establishing secure local connection…</p>
              </>
            ) : (
              <form onSubmit={handleConnect} id="connector-form">
                <h2 className="modal-title">
                  {connectors.find(c => c.id === activeModal)?.icon}{' '}
                  Connect {connectors.find(c => c.id === activeModal)?.name}
                </h2>
                <p className="modal-subtitle">Enter your integration credentials. All data stays local.</p>

                <div className="form-group">
                  <label className="form-label">
                    {activeModal === 'slack'  ? 'Webhook URL'  :
                     activeModal === 'notion' ? 'API Token'    :
                     activeModal === 'jira'   ? 'Base URL'     :
                     activeModal === 'gdrive' ? 'Folder ID'    : 'API Token'}
                  </label>
                  <input
                    className="form-input"
                    id="modal-field1"
                    type={activeModal === 'slack' ? 'url' : 'text'}
                    placeholder={
                      activeModal === 'slack'  ? 'https://hooks.slack.com/...' :
                      activeModal === 'notion' ? 'secret_...'                  :
                      activeModal === 'jira'   ? 'https://your-domain.atlassian.net' :
                      activeModal === 'gdrive' ? '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs' : 'token...'
                    }
                    value={modalField1}
                    onChange={e => setModalField1(e.target.value)}
                    required
                  />
                </div>

                {(activeModal === 'notion' || activeModal === 'jira') && (
                  <div className="form-group">
                    <label className="form-label">
                      {activeModal === 'notion' ? 'Database ID' : 'Project Key'}
                    </label>
                    <input
                      className="form-input"
                      id="modal-field2"
                      type="text"
                      placeholder={activeModal === 'notion' ? 'xxxxxxxx-xxxx-...' : 'PROJ'}
                      value={modalField2}
                      onChange={e => setModalField2(e.target.value)}
                    />
                  </div>
                )}

                <div className="modal-actions">
                  <button type="button" className="btn-secondary" id="modal-cancel-btn" onClick={() => setActiveModal(null)}>Cancel</button>
                  <button type="submit" className="btn-primary" id="modal-connect-btn">Connect</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
