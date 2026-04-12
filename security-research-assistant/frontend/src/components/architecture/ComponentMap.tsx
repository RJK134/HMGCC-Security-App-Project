/** Interactive architecture diagram using pure SVG (no external library dependency). */

import { useState } from "react";

interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  description: string;
  group: string;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (nodeId: string) => void;
}

const GROUP_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  hardware: { bg: "#dbeafe", border: "#3b82f6", text: "#1e40af" },
  software: { bg: "#dcfce7", border: "#22c55e", text: "#166534" },
  protocol: { bg: "#fef3c7", border: "#f59e0b", text: "#92400e" },
};

const DEFAULT_COLOR = { bg: "#f1f5f9", border: "#94a3b8", text: "#334155" };

export function ComponentMap({ nodes, edges, onNodeClick }: Props) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; node: GraphNode } | null>(null);

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center h-64 text-sra-muted text-sm">
        No components extracted yet. Import documents and run extraction.
      </div>
    );
  }

  // Simple force-directed-like layout: arrange nodes in a grid by group
  const grouped: Record<string, GraphNode[]> = {};
  for (const n of nodes) {
    const g = n.group || "other";
    if (!grouped[g]) grouped[g] = [];
    grouped[g].push(n);
  }

  const positions: Record<string, { x: number; y: number }> = {};
  let groupY = 60;

  for (const [, groupNodes] of Object.entries(grouped)) {
    const cols = Math.min(groupNodes.length, 4);
    groupNodes.forEach((node, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      positions[node.id] = {
        x: 100 + col * 200,
        y: groupY + row * 90,
      };
    });
    const rows = Math.ceil(groupNodes.length / 4);
    groupY += rows * 90 + 50;
  }

  const svgWidth = 900;
  const svgHeight = Math.max(groupY + 40, 400);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node.id);
    onNodeClick?.(node.id);
  };

  return (
    <div className="border border-sra-border rounded-lg bg-white dark:bg-gray-900 overflow-auto relative">
      <svg
        width={svgWidth}
        height={svgHeight}
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="w-full"
      >
        {/* Edges */}
        {edges.map((edge, i) => {
          const from = positions[edge.source];
          const to = positions[edge.target];
          if (!from || !to) return null;
          return (
            <g key={`edge-${i}`}>
              <line
                x1={from.x + 75}
                y1={from.y + 25}
                x2={to.x + 75}
                y2={to.y + 25}
                stroke="#94a3b8"
                strokeWidth={1.5}
                markerEnd="url(#arrowhead)"
              />
              {edge.label && (
                <text
                  x={(from.x + to.x) / 2 + 75}
                  y={(from.y + to.y) / 2 + 20}
                  textAnchor="middle"
                  className="text-[9px] fill-gray-500"
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {/* Arrow marker */}
        <defs>
          <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
          </marker>
        </defs>

        {/* Nodes */}
        {nodes.map((node) => {
          const pos = positions[node.id];
          if (!pos) return null;
          const colors = GROUP_COLORS[node.group] ?? DEFAULT_COLOR;
          const isSelected = selectedNode === node.id;

          return (
            <g
              key={node.id}
              onClick={() => handleNodeClick(node)}
              onMouseEnter={(e) => setTooltip({ x: e.clientX, y: e.clientY, node })}
              onMouseLeave={() => setTooltip(null)}
              className="cursor-pointer"
            >
              <rect
                x={pos.x}
                y={pos.y}
                width={150}
                height={50}
                rx={8}
                fill={colors.bg}
                stroke={isSelected ? "#3b82f6" : colors.border}
                strokeWidth={isSelected ? 2.5 : 1.5}
              />
              <text
                x={pos.x + 75}
                y={pos.y + 22}
                textAnchor="middle"
                className="text-[11px] font-medium"
                fill={colors.text}
              >
                {node.label.length > 18 ? node.label.slice(0, 16) + "..." : node.label}
              </text>
              <text
                x={pos.x + 75}
                y={pos.y + 38}
                textAnchor="middle"
                className="text-[9px]"
                fill={colors.text}
                opacity={0.7}
              >
                {node.node_type}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 bg-sra-card border border-sra-border rounded-lg shadow-lg p-2 text-xs max-w-[200px]"
          style={{ left: tooltip.x + 10, top: tooltip.y - 10 }}
        >
          <p className="font-semibold">{tooltip.node.label}</p>
          <p className="text-sra-muted capitalize">{tooltip.node.node_type}</p>
          {tooltip.node.description && (
            <p className="text-sra-muted mt-0.5">{tooltip.node.description}</p>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="flex gap-4 p-2 border-t border-sra-border text-[10px]">
        {Object.entries(GROUP_COLORS).map(([group, colors]) => (
          <div key={group} className="flex items-center gap-1">
            <span className="w-3 h-3 rounded" style={{ background: colors.bg, border: `1px solid ${colors.border}` }} />
            <span className="capitalize">{group}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
