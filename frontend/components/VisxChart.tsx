import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { Bar, LinePath, AreaClosed } from '@visx/shape';
import { scaleBand, scaleLinear, scaleOrdinal } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { GridRows } from '@visx/grid';
import { ParentSize } from '@visx/responsive';
import { LinearGradient } from '@visx/gradient';
import { curveMonotoneX } from '@visx/curve';
import { useTooltip, TooltipWithBounds, defaultStyles } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { LegendOrdinal } from '@visx/legend';

const deepSpaceTheme = {
  axis: 'rgba(255,255,255,0.2)',
  grid: 'rgba(255,255,255,0.05)',
  text: '#94a3b8',
  tooltipBg: 'rgba(10, 15, 25, 0.9)',
};

const tooltipStyles = {
  ...defaultStyles,
  backgroundColor: deepSpaceTheme.tooltipBg,
  color: 'white',
  border: '1px solid rgba(255,255,255,0.1)',
  backdropFilter: 'blur(8px)',
  borderRadius: '8px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
};

interface VisxChartProps {
  data: any[];
}

const Chart = ({ data, width, height }: { data: any[]; width: number; height: number }) => {
  const margin = { top: 40, right: 20, bottom: 40, left: 40 }; // increased top margin for legend
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const {
    showTooltip,
    hideTooltip,
    tooltipData,
    tooltipLeft = 0,
    tooltipTop = 0,
  } = useTooltip<{ x: string; y: number; name: string, color: string }>();

  // Extract shared X axis labels (assuming all traces share the same X axis for simplicity)
  const xValues = data[0]?.x || [];

  // Metadata per trace
  const traceMeta = useMemo(() => {
    return data.map((t, i) => ({
      name: t.name || `Trace ${i + 1}`,
      color: t.marker?.color || (t.type === 'bar' ? '#a855f7' : '#38bdf8'),
      type: t.type
    }));
  }, [data]);

  const legendScale = useMemo(() => scaleOrdinal({
    domain: traceMeta.map(t => t.name),
    range: traceMeta.map(t => t.color),
  }), [traceMeta]);

  // Find max Y across all traces
  const maxY = useMemo(() => {
    let max = 0;
    data.forEach((trace) => {
      const traceMax = Math.max(...(trace.y || []));
      if (traceMax > max) max = traceMax;
    });
    return max * 1.1; // 10% headroom
  }, [data]);

  // Scales
  const xScale = useMemo(
    () =>
      scaleBand<string>({
        range: [0, innerWidth],
        domain: xValues,
        padding: 0.2, // slightly lower padding to allow wider groups
      }),
    [innerWidth, xValues]
  );

  const barNames = traceMeta.filter(t => t.type === 'bar').map(t => t.name);
  
  const xGroupScale = useMemo(() => scaleBand<string>({
    domain: barNames,
    range: [0, xScale.bandwidth() || 1],
    padding: 0.1,
  }), [xScale, barNames]);

  const yScale = useMemo(
    () =>
      scaleLinear<number>({
        range: [innerHeight, 0],
        domain: [0, maxY],
      }),
    [innerHeight, maxY]
  );

  if (innerWidth < 10) return null;

  return (
    <div style={{ position: 'relative' }}>
      <div style={{ position: 'absolute', top: 0, right: margin.right, display: 'flex', zIndex: 10 }}>
        <LegendOrdinal scale={legendScale} direction="row" labelMargin="0 16px 0 8px">
          {(labels) => (
            <div style={{ display: 'flex', flexDirection: 'row' }}>
              {labels.map((label, i) => (
                <div key={`legend-${i}`} style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: deepSpaceTheme.text, fontFamily: 'var(--font-geist-sans), sans-serif' }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: label.value, marginRight: 6, boxShadow: `0 0 6px ${label.value}` }} />
                  {label.text}
                </div>
              ))}
            </div>
          )}
        </LegendOrdinal>
      </div>

      <svg width={width} height={height}>
        {/* Dynamic Area Gradients */}
        {traceMeta.map((t, i) => (
          <LinearGradient key={`grad-${i}`} id={`area-grad-${i}`} from={t.color} to="transparent" fromOpacity={0.3} toOpacity={0} />
        ))}

        <Group left={margin.left} top={margin.top}>
          {/* Grid */}
          <GridRows scale={yScale} width={innerWidth} height={innerHeight} stroke={deepSpaceTheme.grid} />

          {/* Render Traces */}
          {data.map((trace, i) => {
            const isBar = trace.type === 'bar';
            const meta = traceMeta[i];
            
            if (isBar) {
              const barWidth = xGroupScale.bandwidth();
              return (
                <Group key={`trace-${i}`}>
                  {trace.x.map((xVal: string, j: number) => {
                    const yVal = trace.y[j];
                    const barHeight = innerHeight - (yScale(yVal) ?? 0);
                    const groupX = xScale(xVal) ?? 0;
                    const barX = groupX + (xGroupScale(meta.name) ?? 0);
                    const barY = innerHeight - barHeight;

                    return (
                      <Bar
                        key={`bar-${i}-${j}`}
                        x={barX}
                        y={barY}
                        width={barWidth}
                        height={Math.max(0, barHeight)}
                        fill={meta.color}
                        rx={4}
                        onMouseEnter={(event) => {
                          const coords = localPoint(event.currentTarget.ownerSVGElement!, event);
                          showTooltip({
                            tooltipData: { x: xVal, y: yVal, name: meta.name, color: meta.color },
                            tooltipLeft: coords?.x,
                            tooltipTop: coords?.y,
                          });
                        }}
                        onMouseLeave={hideTooltip}
                        style={{ cursor: 'crosshair', filter: `drop-shadow(0 0 6px ${meta.color})` }}
                      />
                    );
                  })}
                </Group>
              );
            } else {
              // Line / Scatter Trace
              const lineData = trace.x.map((xVal: string, j: number) => ({ x: xVal, y: trace.y[j] }));

              return (
                <Group key={`trace-${i}`}>
                  <AreaClosed
                    data={lineData}
                    x={(d) => (xScale(d.x) ?? 0) + xScale.bandwidth() / 2}
                    y={(d) => yScale(d.y) ?? 0}
                    yScale={yScale}
                    fill={`url(#area-grad-${i})`}
                    curve={curveMonotoneX}
                  />
                  <LinePath
                    data={lineData}
                    x={(d) => (xScale(d.x) ?? 0) + xScale.bandwidth() / 2}
                    y={(d) => yScale(d.y) ?? 0}
                    stroke={meta.color}
                    strokeWidth={3}
                    curve={curveMonotoneX}
                    style={{ filter: `drop-shadow(0 0 4px ${meta.color})` }}
                  />
                  {/* Invisible overlay for Line tooltips */}
                  {lineData.map((d: any, j: number) => {
                    const cx = (xScale(d.x) ?? 0) + xScale.bandwidth() / 2;
                    const cy = yScale(d.y) ?? 0;
                    return (
                      <circle
                        key={`point-${i}-${j}`}
                        cx={cx}
                        cy={cy}
                        r={12}
                        fill="transparent"
                        onMouseEnter={(event) => {
                          const coords = localPoint(event.currentTarget.ownerSVGElement!, event);
                          showTooltip({
                            tooltipData: { x: d.x, y: d.y, name: meta.name, color: meta.color },
                            tooltipLeft: coords?.x,
                            tooltipTop: coords?.y,
                          });
                        }}
                        onMouseLeave={hideTooltip}
                        style={{ cursor: 'crosshair' }}
                      />
                    );
                  })}
                </Group>
              );
            }
          })}

          {/* Axes */}
          <AxisBottom
            top={innerHeight}
            scale={xScale}
            stroke={deepSpaceTheme.axis}
            tickStroke={deepSpaceTheme.axis}
            tickLabelProps={() => ({
              fill: deepSpaceTheme.text,
              fontSize: 12,
              textAnchor: 'middle',
              fontFamily: 'var(--font-geist-sans), sans-serif',
            })}
          />
          <AxisLeft
            scale={yScale}
            stroke="transparent"
            tickStroke="transparent"
            numTicks={5}
            tickLabelProps={() => ({
              fill: deepSpaceTheme.text,
              fontSize: 12,
              textAnchor: 'end',
              dx: -10,
              dy: 4,
              fontFamily: 'var(--font-geist-mono), monospace',
            })}
          />
        </Group>
      </svg>
      {tooltipData && (
        <TooltipWithBounds top={tooltipTop} left={tooltipLeft} style={tooltipStyles}>
          <div className="text-sm font-medium flex items-center mb-1">
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: tooltipData.color, marginRight: 6 }} />
            <span className="text-slate-300">{tooltipData.name}</span>
          </div>
          <div className="text-sm font-medium ml-3.5">
            <span className="text-slate-400 mr-2">{tooltipData.x}:</span>
            <span className="text-white font-mono">{tooltipData.y}</span>
          </div>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export function VisxChart({ data }: VisxChartProps) {
  if (!data || !data.length) return null;
  
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ParentSize>
        {({ width, height }) => <Chart data={data} width={width} height={height} />}
      </ParentSize>
    </div>
  );
}
