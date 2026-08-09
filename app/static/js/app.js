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
}

function updateEnergyMetrics(m) {
  const curPwr = document.getElementById("stat-power-curr");
  const basePwr = document.getElementById("stat-power-base");
  const savedKwh = document.getElementById("stat-saved-kwh");
  const savedCost = document.getElementById("stat-saved-cost");
  const effPct = document.getElementById("stat-eff-pct");

  if (curPwr) curPwr.textContent = `${m.current_power_watts} W`;
  if (basePwr) basePwr.textContent = `${m.baseline_power_watts} W`;
  if (savedKwh) savedKwh.textContent = `${m.saved_kwh} kWh`;
  if (savedCost) savedCost.textContent = `$${m.saved_cost_usd.toFixed(2)}`;
  if (effPct) effPct.textContent = `${m.energy_efficiency_pct}%`;

  if (powerChart && powerChart.data) {
    requestAnimationFrame(() => {
      powerChart.data.datasets[0].data.shift();
      powerChart.data.datasets[0].data.push(m.current_power_watts);
      powerChart.data.datasets[1].data.shift();
      powerChart.data.datasets[1].data.push(m.baseline_power_watts);
      powerChart.update('none');
    });
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
  powerChart = new Chart(ctx.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array(30).fill(''),
      datasets: [
        {
          label: 'Actual Draw (W)',
          data: Array(30).fill(0),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
        },
        {
          label: 'Baseline (W)',
          data: Array(30).fill(1305),
          borderColor: '#ef4444',
          borderDash: [5, 5],
          fill: false,
          tension: 0.1,
          borderWidth: 1.5,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: { display: false },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#a1a1aa', font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: '#f4f4f5', font: { size: 11 } } }
      }
    }
  });
}

function bindGlobalEvents() {
  window.toggleDevice = toggleDevice;
}
