/**
 * Keyed DOM Diffing Virtual Device Cards Component (Zero Layout Thrashing)
 * Perplexity-inspired aesthetic: rounded-[32px], font-black headings, micro-animations
 */
export class DeviceListComponent {
  constructor(containerEl, onToggle, onDelete) {
    this.container = containerEl;
    this.onToggle = onToggle;
    this.onDelete = onDelete;
    this.nodesMap = new Map(); // Keyed node cache: device_id -> DOM element
  }

  update(deviceStates, deviceTelemetry, deviceTimeouts) {
    const activeKeys = new Set(Object.keys(deviceStates));

    // Remove deleted devices
    for (const [id, node] of this.nodesMap.entries()) {
      if (!activeKeys.has(id)) {
        node.remove();
        this.nodesMap.delete(id);
      }
    }

    // Keyed surgical patch or creation
    for (const [id, state] of Object.entries(deviceStates)) {
      const pwrPct = deviceTelemetry?.[id]?.power_pct ?? (state === "ON" ? 100 : (state === "DIM" ? 30 : 0));
      const isRamping = deviceTelemetry?.[id]?.is_ramping ?? false;
      const timeout = deviceTimeouts?.[id] ?? 10;
      const isOn = state === "ON" || state === "DIM";

      let displayStatus = state;
      if (isRamping) {
        displayStatus = isOn ? "RAMPING UP" : "RAMPING DOWN";
      }

      if (!this.nodesMap.has(id)) {
        const el = this.createDeviceNode(id, state, displayStatus, pwrPct, isRamping, timeout, isOn);
        this.container.appendChild(el);
        this.nodesMap.set(id, el);
      } else {
        this.patchDeviceNode(this.nodesMap.get(id), state, displayStatus, pwrPct, isRamping, timeout, isOn);
      }
    }
  }

  createDeviceNode(id, state, displayStatus, pwrPct, isRamping, timeout, isOn) {
    const card = document.createElement("div");
    card.id = `device-card-${id}`;
    card.className = "glass-panel p-4 rounded-[24px] border border-zinc-800/80 flex flex-col gap-3 glass-panel-hover transition-all-300 shadow-lg";

    const labelName = id.replace(/_/g, " ").toUpperCase();
    const actionLabel = isOn ? "Turn Off" : "Turn On";

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3.5">
          <div class="device-icon-box p-3 ${isOn ? 'bg-emerald-500/20 text-emerald-300' : 'bg-zinc-800/40 text-zinc-600'} rounded-2xl transition-all-300">
            <i class="fa-solid ${id.includes('ac') || id.includes('hvac') ? 'fa-snowflake' : (id.includes('fan') ? 'fa-fan' : (id.includes('light') || id.includes('lamp') ? 'fa-lightbulb' : 'fa-plug'))} text-lg"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h4 class="text-sm font-black-heading text-zinc-100 tracking-wide">${labelName}</h4>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-mono bg-zinc-900 text-zinc-400 border border-zinc-800">${timeout}s Auto-Off</span>
            </div>
            <p class="device-state-text text-xs ${isRamping ? 'text-amber-400 animate-pulse' : (isOn ? 'text-emerald-400' : 'text-zinc-500')} font-semibold mt-0.5">
              Status: ${displayStatus} (${pwrPct}%)
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button class="device-toggle-btn px-4 py-2 rounded-xl text-xs font-bold transition-all-300 ${isOn ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30 hover:bg-rose-500/20' : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/20'} flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid ${isOn ? 'fa-power-off text-rose-400' : 'fa-bolt text-emerald-400'}"></i> ${actionLabel}
          </button>
          ${this.onDelete ? `
            <button class="device-delete-btn p-2 rounded-xl text-zinc-600 hover:text-rose-400 hover:bg-rose-500/10 transition-all-300">
              <i class="fa-solid fa-trash text-xs"></i>
            </button>
          ` : ''}
        </div>
      </div>

      <!-- Power Ramp Telemetry Bar -->
      <div class="w-full bg-zinc-950/80 rounded-full h-2 border border-zinc-800/80 overflow-hidden relative">
        <div class="power-ramp-fill bg-gradient-to-r ${isOn ? 'from-emerald-500 to-teal-400' : 'from-zinc-700 to-zinc-600'} h-full rounded-full transition-all-300" style="width: ${pwrPct}%"></div>
      </div>
    `;

    const toggleBtn = card.querySelector(".device-toggle-btn");
    toggleBtn.addEventListener("click", () => {
      if (this.onToggle) this.onToggle(id);
    });

    const deleteBtn = card.querySelector(".device-delete-btn");
    if (deleteBtn && this.onDelete) {
      deleteBtn.addEventListener("click", () => this.onDelete(id));
    }

    return card;
  }

  patchDeviceNode(node, state, displayStatus, pwrPct, isRamping, timeout, isOn) {
    const stateEl = node.querySelector(".device-state-text");
    const iconContainer = node.querySelector(".device-icon-box");
    const toggleBtn = node.querySelector(".device-toggle-btn");
    const rampFill = node.querySelector(".power-ramp-fill");

    const newStatusText = `Status: ${displayStatus} (${pwrPct}%)`;
    if (stateEl.textContent !== newStatusText) {
      stateEl.textContent = newStatusText;
      stateEl.className = `device-state-text text-xs ${isRamping ? 'text-amber-400 animate-pulse' : (isOn ? 'text-emerald-400' : 'text-zinc-500')} font-semibold mt-0.5`;
    }

    iconContainer.className = `device-icon-box p-3 ${isOn ? 'bg-emerald-500/20 text-emerald-300' : 'bg-zinc-800/40 text-zinc-600'} rounded-2xl transition-all-300`;

    const actionLabel = isOn ? "Turn Off" : "Turn On";
    toggleBtn.className = `device-toggle-btn px-4 py-2 rounded-xl text-xs font-bold transition-all-300 ${isOn ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30 hover:bg-rose-500/20' : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/20'} flex items-center gap-1.5 shadow-sm`;
    toggleBtn.innerHTML = `<i class="fa-solid ${isOn ? 'fa-power-off text-rose-400' : 'fa-bolt text-emerald-400'}"></i> ${actionLabel}`;

    if (rampFill) {
      rampFill.style.width = `${pwrPct}%`;
      rampFill.className = `power-ramp-fill bg-gradient-to-r ${isOn ? 'from-emerald-500 to-teal-400' : 'from-zinc-700 to-zinc-600'} h-full rounded-full transition-all-300`;
    }
  }
}

