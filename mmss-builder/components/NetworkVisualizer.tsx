import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { MMSSRoot } from '../types';

interface NetworkVisualizerProps {
  data: MMSSRoot | null;
}

interface Node extends d3.SimulationNodeDatum {
  id: string;
  group: string;
  val: number;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string | Node;
  target: string | Node;
  type: string;
}

const NetworkVisualizer: React.FC<NetworkVisualizerProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 400 });

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    
    window.addEventListener('resize', updateSize);
    updateSize();
    
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous

    const width = dimensions.width;
    const height = dimensions.height;

    // --- Prepare Data ---
    const nodes: Node[] = [];
    const links: Link[] = [];

    // Central System Node
    const systemId = data.MMSS_UNIVERSAL_TEMPLATE.meta.system_id || "System";
    nodes.push({ id: systemId, group: "core", val: 20 });

    // State Variables (X)
    const xDesc = data.MMSS_UNIVERSAL_TEMPLATE.STATE_SPACE.X;
    nodes.push({ id: "State (X)", group: "state", val: 15 });
    links.push({ source: systemId, target: "State (X)", type: "part_of" });

    // Individual examples as leaf nodes for X
    xDesc.examples.forEach((ex, i) => {
      const id = `X_${i}`;
      nodes.push({ id: ex, group: "variable", val: 5 });
      links.push({ source: "State (X)", target: ex, type: "defines" });
    });

    // Inputs (U)
    nodes.push({ id: "Inputs (U)", group: "input", val: 12 });
    links.push({ source: systemId, target: "Inputs (U)", type: "part_of" });
    data.MMSS_UNIVERSAL_TEMPLATE.STATE_SPACE.U.examples.forEach((ex) => {
      nodes.push({ id: ex, group: "variable", val: 5 });
      links.push({ source: "Inputs (U)", target: ex, type: "defines" });
    });

    // Outputs (Y)
    nodes.push({ id: "Outputs (Y)", group: "output", val: 12 });
    links.push({ source: systemId, target: "Outputs (Y)", type: "part_of" });
    data.MMSS_UNIVERSAL_TEMPLATE.STATE_SPACE.Y.examples.forEach((ex) => {
      nodes.push({ id: ex, group: "variable", val: 5 });
      links.push({ source: "Outputs (Y)", target: ex, type: "defines" });
    });

    // Flows/Storages
    data.MMSS_UNIVERSAL_TEMPLATE.FLOWS_AND_BALANCES.storages.forEach((storage) => {
        nodes.push({ id: storage.name, group: "storage", val: 10 });
        links.push({ source: systemId, target: storage.name, type: "contains" });
    });

    // Controls
    data.MMSS_UNIVERSAL_TEMPLATE.CONTROLS_AND_FEEDBACK.feedback_loops.forEach((loop) => {
        nodes.push({ id: loop.name, group: "control", val: 8 });
        // Controls usually connect Output to Input (conceptually), but here we link to System
        links.push({ source: loop.name, target: systemId, type: "regulates" });
    });


    // --- Simulation ---
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(30));

    // --- Drawing ---
    const link = svg.append("g")
      .attr("stroke", "#475569")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1.5);

    const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (d) => Math.sqrt(d.val) * 4)
      .attr("fill", (d) => {
        if (d.group === "core") return "#ef4444"; // Red
        if (d.group === "state") return "#3b82f6"; // Blue
        if (d.group === "variable") return "#94a3b8"; // Gray
        if (d.group === "storage") return "#eab308"; // Yellow
        if (d.group === "control") return "#10b981"; // Green
        return "#64748b";
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    const labels = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .text(d => d.id.length > 20 ? d.id.substring(0, 20) + '...' : d.id)
        .attr("font-size", "10px")
        .attr("fill", "#e2e8f0")
        .attr("dx", 12)
        .attr("dy", 4);

    node.append("title")
      .text(d => d.id);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);
      
      labels
        .attr("x", (d: any) => d.x)
        .attr("y", (d: any) => d.y);
    });

    function dragstarted(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }, [data, dimensions]);

  if (!data) {
    return (
      <div ref={containerRef} className="w-full h-full flex items-center justify-center text-slate-500 border border-slate-700 rounded-lg bg-slate-900/50">
        <p className="font-mono text-sm">Visualize system topology here...</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full relative border border-slate-700 rounded-lg bg-slate-900 overflow-hidden shadow-inner">
        <div className="absolute top-2 left-2 z-10 bg-slate-800/80 p-2 rounded text-xs font-mono space-y-1 backdrop-blur-sm pointer-events-none">
            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>System</div>
            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>State</div>
            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>Storage</div>
            <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>Control</div>
        </div>
      <svg ref={svgRef} className="w-full h-full cursor-move" width={dimensions.width} height={dimensions.height}></svg>
    </div>
  );
};

export default NetworkVisualizer;