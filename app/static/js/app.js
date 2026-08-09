import { RobustWebSocket } from './ws-client.js';
import { getNormalizedVideoCoordinates } from './utils/projection.js';
import { DeviceListComponent } from './components/device-list.js';

let wsClient;
let deviceListComponent;
let powerChart;
let isHeatmapActive = false;
let isDrawing = false;
let startX, startY, endX, endY;
let drawnBbox = [0, 0, 1, 1];
let currentDeviceStates = {};

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("device-list-container");
  if (container) {
    deviceListComponent = new DeviceListComponent(
      container,
      (deviceId) => toggleDevice(deviceId),
      (deviceId) => {
        if (window.deleteDevice) {
          window.deleteDevice(deviceId);
        }
      }
    );
  }

  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/status`;

  wsClient = new RobustWebSocket(
    wsUrl,
    (data) => updateDashboard(data),
    (status) => updateConnectionBadge(status)
  );
  wsClient.connect();

  initChart();
  bindGlobalEvents();
});

function updateConnectionBadge(status) {
  const badge = document.getElementById("connection-badge");
  if (!badge) return;

  if (status === 'CONNECTED') {
    badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 shadow-sm";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Connected`;
  } else if (status === 'CONNECTING') {
    badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1.5 shadow-sm";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span> Connecting to room sensor...`;
  } else {
    badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1.5 shadow-sm";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span> Connection Lost — Reconnecting...`;
  }
}

function updateDashboard(data) {
  if (data.occupant_count !== undefined) {
    const el = document.getElementById("stat-occupants");
    if (el) el.textContent = data.occupant_count;
  }
  if (data.occupancy_status !== undefined) {
    const el = document.getElementById("stat-status");
    if (el) {
      el.textContent = data.occupancy_status;
      el.className = `text-xl font-black-heading ${data.occupancy_status === 'Occupied' ? 'text-emerald-400' : 'text-amber-400'} mt-2`;
    }
  }
  if (data.empty_duration_sec !== undefined) {
    const el = document.getElementById("stat-empty-dur");
    if (el) el.textContent = `${data.empty_duration_sec.toFixed(1)}s`;
  }
  if (data.seconds_until_empty !== undefined) {
    const el = document.getElementById("stat-countdown");
    if (el) el.textContent = `${data.seconds_until_empty.toFixed(1)}s`;
  }

  if (data.device_states && deviceListComponent) {
    currentDeviceStates = data.device_states;
    const zeroNotice = document.getElementById("zero-device-notice");
    if (Object.keys(data.device_states).length === 0) {
      if (zeroNotice) zeroNotice.classList.remove("hidden");
    } else {
      if (zeroNotice) zeroNotice.classList.add("hidden");
    }
    deviceListComponent.update(data.device_states, data.device_telemetry, data.device_countdowns);
  }


  if (data.energy_metrics) {
    updateEnergyMetrics(data.energy_metrics);
  }

  if (data.forecast) {
    updateForecast(data.forecast);
  }

  if (data.event_logs) {
    updateEventLogs(data.event_logs);
  }
}

function updateEventLogs(logs) {
  const container = document.getElementById("event-log-rows");
  const badge = document.getElementById("audit-log-badge");

  if (badge) {
    badge.textContent = logs ? logs.length : 0;
  }

  if (!container) return;

  if (!logs || logs.length === 0) {
    container.innerHTML = `
      <tr>
        <td colspan="4" class="py-6 text-center text-zinc-600">
          No events logged yet.
        </td>
      </tr>
    `;
    return;
  }

  let html = "";
  for (const log of logs) {
    const timeStr = log.timestamp ? new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—";
    const deviceName = log.device_id ? log.device_id.toUpperCase() : (log.action === "CONFIG_UPDATE" ? "SYSTEM" : "N/A");
    const action = log.action || "UPDATE";
    const reason = log.reason || log.details || "System Event";
    const status = log.status || "CONFIRMED";

    let actionBadgeClass = "bg-zinc-800 text-zinc-300 border-zinc-700";
    if (action === "ON" || action === "TURN_ON") {
      actionBadgeClass = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    } else if (action === "DIM") {
      actionBadgeClass = "bg-amber-500/20 text-amber-400 border-amber-500/30";
    } else if (action === "OFF" || action === "TURN_OFF") {
      actionBadgeClass = "bg-rose-500/20 text-rose-400 border-rose-500/30";
    } else if (action === "CONFIG_UPDATE") {
      actionBadgeClass = "bg-sky-500/20 text-sky-400 border-sky-500/30";
    }

    let statusDot = "";
    if (status === "PENDING") {
      statusDot = `<span class="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse mr-1"></span>`;
    } else if (status === "CONFIRMED") {
      statusDot = `<span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1"></span>`;
    }

    html += `
      <tr class="hover:bg-zinc-800/30 transition-colors">
        <td class="py-2.5 font-mono text-[11px] text-zinc-400">${timeStr}</td>
        <td class="py-2.5 font-semibold text-zinc-200">${deviceName}</td>
        <td class="py-2.5">
          <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${actionBadgeClass}">
            ${statusDot}${action}
          </span>
        </td>
        <td class="py-2.5 text-zinc-400 text-[11px] truncate max-w-[150px]" title="${reason}">${reason}</td>
      </tr>
    `;
  }

  container.innerHTML = html;
}

let lastAnalyticsFetch = 0;

function updateEnergyMetrics(m) {
  const curPwr = document.getElementById("stat-power-draw");
  const basePwr = document.getElementById("stat-baseline-power");
  const savedKwh = document.getElementById("stat-saved-kwh");
  const savedCo2 = document.getElementById("stat-saved-co2");
  const savedCost = document.getElementById("stat-saved-cost");
  const effPct = document.getElementById("stat-efficiency");

  if (curPwr && m.current_power_watts !== undefined) curPwr.textContent = `${m.current_power_watts.toFixed(1)} W`;
  if (basePwr && m.baseline_power_watts !== undefined) basePwr.textContent = `${m.baseline_power_watts.toFixed(0)} W`;
  if (savedKwh && m.saved_kwh !== undefined) savedKwh.textContent = `${m.saved_kwh.toFixed(4)} kWh`;
  if (savedCo2 && m.saved_co2_kg !== undefined) savedCo2.textContent = `${m.saved_co2_kg.toFixed(2)} kg`;
  if (savedCost && m.saved_cost_usd !== undefined) savedCost.textContent = `$${m.saved_cost_usd.toFixed(2)}`;
  if (effPct && m.energy_efficiency_pct !== undefined) effPct.textContent = `${m.energy_efficiency_pct.toFixed(1)}%`;

  // Periodically refresh 24-hour analytics chart every 30 seconds
  const now = Date.now();
  if (now - lastAnalyticsFetch > 30000) {
    lastAnalyticsFetch = now;
    fetchAnalyticsData();
  }
}

async function fetchAnalyticsData() {
  try {
    const [hourlyRes, dailyRes] = await Promise.all([
      fetch("/api/analytics/hourly/today"),
      fetch("/api/analytics/daily/today")
    ]);

    if (!hourlyRes.ok || !dailyRes.ok) return;

    const hourlyData = await hourlyRes.json();
    const dailyData = await dailyRes.json();

    if (hourlyData && hourlyData.hourly_summary && powerChart) {
      const hourly = hourlyData.hourly_summary;
      const actuals = hourly.map(h => h.kwh_actual);
      const baselines = hourly.map(h => h.kwh_baseline);

      const actualColors = hourly.map(h => h.schedule_active ? 'rgba(16, 185, 129, 0.85)' : 'rgba(161, 161, 170, 0.4)');
      const baselineColors = hourly.map(h => h.schedule_active ? 'rgba(56, 189, 248, 0.85)' : 'rgba(113, 113, 122, 0.3)');

      powerChart.data.datasets[0].data = actuals;
      powerChart.data.datasets[0].backgroundColor = actualColors;
      powerChart.data.datasets[1].data = baselines;
      powerChart.data.datasets[1].backgroundColor = baselineColors;
      powerChart.update();
    }

    if (dailyData) {
      const peakDemandEl = document.getElementById("insight-peak-demand");
      if (peakDemandEl) {
        const peakHourFormatted = dailyData.peak_hour !== undefined ? (dailyData.peak_hour === 0 ? '12 AM' : dailyData.peak_hour < 12 ? `${dailyData.peak_hour} AM` : dailyData.peak_hour === 12 ? '12 PM' : `${dailyData.peak_hour - 12} PM`) : '--';
        peakDemandEl.textContent = `${(dailyData.peak_power_watts || 0).toFixed(1)} W at ${peakHourFormatted}`;
      }

      const peakSavingsEl = document.getElementById("insight-peak-savings");
      if (peakSavingsEl) {
        peakSavingsEl.textContent = `${(dailyData.total_kwh_saved || 0).toFixed(2)} kWh Saved Today`;
      }

      const deviceListEl = document.getElementById("device-usage-list");
      if (deviceListEl) {
        const usageHours = dailyData.device_usage_hours || {};
        const devKeys = Object.keys(usageHours);
        if (devKeys.length === 0) {
          deviceListEl.innerHTML = `<span class="text-zinc-500 italic">No device usage recorded yet today.</span>`;
        } else {
          deviceListEl.innerHTML = devKeys.map(dev => {
            const hrs = usageHours[dev];
            const pct = Math.min(100, Math.round((hrs / 24.0) * 100));
            return `
              <div class="flex justify-between items-center">
                <span class="font-bold text-zinc-200 capitalize">${dev}</span>
                <span class="text-emerald-400 font-mono">${hrs.toFixed(1)} hrs (${pct}% of day)</span>
              </div>
            `;
          }).join("");
        }
      }
    }
  } catch (err) {
    console.error("Error fetching 24-hour analytics:", err);
  }
}

function downloadCSVReport() {
  window.location.href = "/api/analytics/export/csv";
}

async function toggleWeeklyModal() {
  try {
    const res = await fetch("/api/analytics/weekly");
    if (!res.ok) return;
    const data = await res.json();
    const trend = data.weekly_trend || [];
    let summaryText = "7-Day Energy Analytics Trend:\n\n";
    for (const day of trend) {
      summaryText += `${day.date}: Saved ${day.total_kwh_saved.toFixed(2)} kWh ($${day.total_cost_saved_usd.toFixed(2)}) | Efficiency: ${day.savings_percentage.toFixed(1)}%\n`;
    }
    alert(summaryText);
  } catch (err) {
    console.error("Error fetching weekly trend:", err);
  }
}

function updateForecast(forecast) {
  const forecastEl = document.getElementById("stat-forecast");
  if (!forecastEl || !forecast) return;

  if (forecast.prewarm_hvac_recommended || forecast.prewarm_lighting_recommended) {
    forecastEl.textContent = "Pre-warm Rec.";
    forecastEl.className = "text-emerald-400 font-bold";
  } else {
    forecastEl.textContent = "Normal";
    forecastEl.className = "text-amber-300";
  }
}

function toggleDevice(deviceId) {
  const currentState = currentDeviceStates[deviceId] || "OFF";
  const targetState = (currentState === "ON" || currentState === "DIM") ? "OFF" : "ON";
  if (wsClient) {
    wsClient.send({
      type: "TOGGLE_DEVICE",
      device_id: deviceId,
      state: targetState
    });
  }
}

function initChart() {
  const ctx = document.getElementById('powerChart');
  if (!ctx) return;
  const labels = [
    '12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM',
    '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM',
    '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM'
  ];

  powerChart = new Chart(ctx.getContext('2d'), {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Actual kWh',
          data: Array(24).fill(0),
          backgroundColor: 'rgba(16, 185, 129, 0.85)',
          borderRadius: 6,
          borderWidth: 0,
        },
        {
          label: 'Baseline kWh',
          data: Array(24).fill(0),
          backgroundColor: 'rgba(56, 189, 248, 0.85)',
          borderRadius: 6,
          borderWidth: 0,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 500 },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#a1a1aa', font: { size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#a1a1aa', font: { size: 10 } },
          title: { display: true, text: 'Energy (kWh)', color: '#71717a', font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: '#f4f4f5', font: { size: 11 } } }
      }
    }
  });

  fetchAnalyticsData();
}

function bindGlobalEvents() {
  window.toggleDevice = toggleDevice;
  window.downloadCSVReport = downloadCSVReport;
  window.toggleWeeklyModal = toggleWeeklyModal;
}

