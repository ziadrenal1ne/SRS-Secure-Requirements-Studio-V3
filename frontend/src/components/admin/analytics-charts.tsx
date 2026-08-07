"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";
import { monthlyGenerated, departmentDistribution, securityScoreTrend } from "@/lib/mock-data";

const pieColors = ["#2563eb", "#10b981", "#d97706", "#8b5cf6"];

function tooltipStyle() {
  return {
    borderRadius: 12,
    border: "1px solid var(--border)",
    background: "var(--surface)",
    fontSize: 12,
    boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
  };
}

function GeneratedDocumentsChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={monthlyGenerated}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
        <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
        <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} width={24} />
        <Tooltip contentStyle={tooltipStyle()} cursor={{ fill: "var(--surface-2)" }} />
        <Bar dataKey="documents" name="Documents générés" fill="#2563eb" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function DepartmentDistributionChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={departmentDistribution} dataKey="value" nameKey="name" innerRadius={55} outerRadius={80} paddingAngle={3}>
          {departmentDistribution.map((entry, i) => (
            <Cell key={entry.name} fill={pieColors[i % pieColors.length]} stroke="none" />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle()} />
      </PieChart>
    </ResponsiveContainer>
  );
}

function SecurityScoreTrendChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={securityScoreTrend}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
        <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
        <YAxis domain={[40, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} width={28} />
        <Tooltip contentStyle={tooltipStyle()} />
        <Line type="monotone" dataKey="score" name="Score moyen" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3.5, fill: "#10b981" }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export { GeneratedDocumentsChart, DepartmentDistributionChart, SecurityScoreTrendChart, pieColors };
