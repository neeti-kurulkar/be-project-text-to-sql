import { useState } from 'react';
import { User, Bot, Code, Table, Copy, Check, Lightbulb, BarChart3, Download, Clock } from 'lucide-react';
import { type QueryMessage as QueryMessageType } from '../../types/query';
import { QueryResults } from './QueryResults';
import { Button } from '../common/Button';
import { exportToCSV } from '../../utils/exportCSV';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface QueryMessageProps {
  message: QueryMessageType;
}

export function QueryMessage({ message }: QueryMessageProps) {
  const [showSQL, setShowSQL] = useState(false);
  const [showTable, setShowTable] = useState(false);
  const [showInsights, setShowInsights] = useState(true);
  const [showChart, setShowChart] = useState(true);
  const [copied, setCopied] = useState(false);

  const isUser = message.type === 'user';

  const handleCopySQL = () => {
    if (message.sql) {
      navigator.clipboard.writeText(message.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportCSV = () => {
    if (message.results) {
      exportToCSV(message.results.rows, message.results.columns, 'query_results');
    }
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="flex items-start gap-3 max-w-3xl">
          <div className="flex-1 bg-electric-500 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm">{message.content}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-electric-500 text-white flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5" />
          </div>
        </div>
      </div>
    );
  }

  // Render chart based on visualization config
  const renderChart = () => {
    if (!message.visualization?.should_visualize || !message.visualization?.chart_config) {
      return null;
    }

    const { chart_type, chart_config } = message.visualization;
    const data = chart_config.data || [];
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];

    if (chart_type === 'bar') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey={chart_config.x_axis?.dataKey}
              tick={{ fontSize: 12, fill: '#9ca3af' }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: '#9ca3af' }}
              domain={[0, 'auto']}
              tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              labelStyle={{ color: '#f3f4f6' }}
              formatter={(value: number) => [value.toLocaleString(), '']}
            />
            <Legend />
            {chart_config.bars?.map((bar, index) => (
              <Bar
                key={bar.dataKey}
                dataKey={bar.dataKey}
                fill={bar.fill || colors[index]}
                name={bar.name}
                isAnimationActive
                animationBegin={0}
                animationDuration={700}
                animationEasing="ease-out"
              />
            )) || (
              <Bar
                dataKey={chart_config.y_axis?.dataKey}
                fill="#3b82f6"
                isAnimationActive
                animationBegin={0}
                animationDuration={700}
                animationEasing="ease-out"
              />
            )}
          </BarChart>
        </ResponsiveContainer>
      );
    }

    if (chart_type === 'line') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey={chart_config.x_axis?.dataKey}
              tick={{ fontSize: 12, fill: '#9ca3af' }}
            />
            <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            {chart_config.lines?.map((line, index) => (
              <Line
                key={line.dataKey}
                type="monotone"
                dataKey={line.dataKey}
                stroke={line.stroke || colors[index]}
                name={line.name}
                strokeWidth={2}
              />
            )) || <Line type="monotone" dataKey={chart_config.y_axis?.dataKey} stroke="#3b82f6" strokeWidth={2} />}
          </LineChart>
        </ResponsiveContainer>
      );
    }

    if (chart_type === 'pie') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              dataKey={chart_config.dataKey}
              nameKey={chart_config.nameKey}
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    return null;
  };

  return (
    <div className="flex justify-start">
      <div className="flex items-start gap-3 max-w-4xl w-full">
        <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex-1 space-y-3">
          {/* Summary/Explanation */}
          <div className="bg-slate-100 dark:bg-ocean-800 rounded-2xl rounded-tl-sm px-4 py-3">
            <p className="text-sm text-ocean-900 dark:text-slate-100">
              {message.insights?.summary || message.results?.explanation || message.content}
            </p>
          </div>

          {/* Key Insights */}
          {message.insights?.key_insights && message.insights.key_insights.length > 0 && showInsights && (
            <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300">Key Insights</span>
              </div>
              <ul className="space-y-1.5">
                {message.insights.key_insights.map((insight, index) => (
                  <li key={index} className="text-sm text-emerald-800 dark:text-emerald-200 flex items-start gap-2">
                    <span className="text-emerald-500">-</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Visualization */}
          {message.visualization?.should_visualize && message.visualization?.chart_config && showChart && (
            <div className="bg-white dark:bg-ocean-800 border border-slate-200 dark:border-ocean-700 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <BarChart3 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  {message.visualization.chart_config.title || 'Visualization'}
                </span>
              </div>
              {renderChart()}
            </div>
          )}

          {/* Toggle Buttons */}
          {(message.sql || message.results || message.insights) && (
            <div className="flex flex-wrap gap-2">
              {message.sql && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSQL(!showSQL)}
                  className="flex items-center gap-2"
                >
                  <Code className="w-4 h-4" />
                  {showSQL ? 'Hide' : 'Show'} SQL
                </Button>
              )}
              {message.results && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowTable(!showTable)}
                  className="flex items-center gap-2"
                >
                  <Table className="w-4 h-4" />
                  {showTable ? 'Hide' : 'Show'} Table ({message.results.rowCount} rows)
                </Button>
              )}
              {message.insights?.key_insights && message.insights.key_insights.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowInsights(!showInsights)}
                  className="flex items-center gap-2"
                >
                  <Lightbulb className="w-4 h-4" />
                  {showInsights ? 'Hide' : 'Show'} Insights
                </Button>
              )}
              {message.visualization?.should_visualize && message.visualization?.chart_config && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowChart(!showChart)}
                  className="flex items-center gap-2"
                >
                  <BarChart3 className="w-4 h-4" />
                  {showChart ? 'Hide' : 'Show'} Chart
                </Button>
              )}
              {message.results && message.results.rows.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleExportCSV}
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </Button>
              )}
            </div>
          )}

          {/* SQL Code Block */}
          {message.sql && showSQL && (
            <div className="bg-ocean-900 rounded-lg overflow-hidden border border-ocean-700">
              <div className="flex items-center justify-between px-4 py-2 border-b border-ocean-700">
                <span className="text-xs font-mono text-slate-400">SQL Query</span>
                <button
                  onClick={handleCopySQL}
                  className="flex items-center gap-1.5 px-2 py-1 text-xs text-slate-400 hover:text-slate-100 transition-colors duration-200"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <pre className="p-4 overflow-x-auto">
                <code className="text-sm text-slate-100 font-mono whitespace-pre-wrap break-words">
                  {message.sql}
                </code>
              </pre>
            </div>
          )}

          {/* Results Table */}
          {message.results && showTable && (
            <QueryResults results={message.results} />
          )}

          {/* Timestamp and Execution Time */}
          <div className="flex items-center gap-3 text-xs text-ocean-600 dark:text-slate-400">
            <span>{formatTime(message.timestamp)}</span>
            {message.executionTime && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {message.executionTime.toFixed(2)}s
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
