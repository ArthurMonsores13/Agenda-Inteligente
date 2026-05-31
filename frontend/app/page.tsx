"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CalendarClock,
  CheckCircle2,
  Plus,
  RefreshCw,
  Stethoscope,
  Trash2,
  X,
  XCircle
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Appointment = {
  id: number;
  patient_name: string;
  phone: string;
  appointment_date: string;
  appointment_time: string;
  service: string;
  status: "Pendente" | "Confirmado" | "Cancelado";
  cancellation_reason: string;
  finalized_at: string | null;
};

type AppointmentForm = {
  patient_name: string;
  phone: string;
  appointment_date: string;
  appointment_time: string;
  service: string;
};

type PeriodFilter = "Todos" | "Hoje" | "Semana" | "Mês";
type ViewMode = "active" | "finalized";

const emptyForm: AppointmentForm = {
  patient_name: "",
  phone: "",
  appointment_date: "",
  appointment_time: "",
  service: ""
};

const statusGroups: Array<{ key: Appointment["status"]; label: string; tone: string }> = [
  { key: "Pendente", label: "Pendente", tone: "pendente" },
  { key: "Confirmado", label: "Confirmado", tone: "confirmado" },
  { key: "Cancelado", label: "Cancelado", tone: "cancelado" }
];

export default function DashboardPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [form, setForm] = useState<AppointmentForm>(emptyForm);
  const [periodFilter, setPeriodFilter] = useState<PeriodFilter>("Hoje");
  const [viewMode, setViewMode] = useState<ViewMode>("active");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  async function loadData(scope = viewMode) {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/appointments/?scope=${scope}`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Nao foi possivel carregar os agendamentos.");
      }
      setAppointments(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado ao carregar.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [viewMode]);

  const filteredAppointments = useMemo(() => {
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const endOfDay = new Date(startOfDay);
    endOfDay.setDate(endOfDay.getDate() + 1);

    const startOfWeek = new Date(startOfDay);
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 7);

    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);

    return appointments.filter((appointment) => {
      if (periodFilter === "Todos") return true;
      const date = new Date(`${appointment.appointment_date}T00:00:00`);
      if (Number.isNaN(date.getTime())) return false;
      if (periodFilter === "Hoje") return date >= startOfDay && date < endOfDay;
      if (periodFilter === "Semana") return date >= startOfWeek && date < endOfWeek;
      return date >= startOfMonth && date < endOfMonth;
    });
  }, [appointments, periodFilter]);

  const grouped = useMemo(() => {
    const map: Record<Appointment["status"], Appointment[]> = {
      Pendente: [],
      Confirmado: [],
      Cancelado: []
    };
    filteredAppointments.forEach((appointment) => {
      map[appointment.status]?.push(appointment);
    });
    return map;
  }, [filteredAppointments]);

  async function createAppointment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const response = await fetch(`${API_URL}/api/appointments/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, status: "Pendente" })
    });

    if (!response.ok) {
      setError("Nao foi possivel criar o agendamento.");
      return;
    }

    setForm(emptyForm);
    setIsModalOpen(false);
    await loadData();
  }

  async function updateStatus(appointment: Appointment, status: Appointment["status"]) {
    const response = await fetch(`${API_URL}/api/appointments/${appointment.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status,
        cancellation_reason: status === "Cancelado" ? appointment.cancellation_reason || "Cancelado pelo gestor" : ""
      })
    });

    if (!response.ok) {
      setError("Nao foi possivel atualizar o status.");
      return;
    }
    await loadData();
  }

  async function deleteAppointment(id: number) {
    const response = await fetch(`${API_URL}/api/appointments/${id}/`, { method: "DELETE" });
    if (!response.ok) {
      setError("Nao foi possivel excluir o agendamento.");
      return;
    }
    await loadData();
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brandIcon">
            <Stethoscope size={20} />
          </span>
          <div>
            <p className="eyebrow">Clinica</p>
            <h1>Gerenciador de Consultas</h1>
          </div>
        </div>
        <div className="topbarActions">
          <button className="iconButton" onClick={() => loadData()} aria-label="Atualizar">
            <RefreshCw size={16} />
          </button>
          <button className="primaryButton" onClick={() => setIsModalOpen(true)}>
            <Plus size={16} />
            Adicionar consulta
          </button>
        </div>
      </header>

      {error ? <div className="alert">{error}</div> : null}

      <section className="filterCard">
        <div className="filterCardHeader">
          <span className="filterLabel">Periodo</span>
          <span className="pill">
            {filteredAppointments.length} {filteredAppointments.length === 1 ? "consulta" : "consultas"}
          </span>
        </div>
        <div className="segmentedControl">
          <button className={viewMode === "active" ? "active" : ""} onClick={() => setViewMode("active")}>
            Ativas
          </button>
          <button className={viewMode === "finalized" ? "active" : ""} onClick={() => setViewMode("finalized")}>
            Finalizadas
          </button>
        </div>
        <div className="segmentedControl">
          {(["Hoje", "Semana", "Mês", "Todos"] as PeriodFilter[]).map((period) => (
            <button
              className={periodFilter === period ? "active" : ""}
              key={period}
              onClick={() => setPeriodFilter(period)}
            >
              {period}
            </button>
          ))}
        </div>
      </section>

      <section className="boardSection" aria-busy={isLoading}>
        {viewMode === "finalized" ? (
          <div className="statusGroup">
            <header className="statusGroupHeader finalizado">
              <span className="statusDot finalizado" />
              <h2>Finalizadas</h2>
              <span className="countBadge">{filteredAppointments.length}</span>
            </header>

            {filteredAppointments.length === 0 ? (
              <div className="emptyState">Nenhuma consulta finalizada ainda.</div>
            ) : (
              <div className="cardsGrid">
                {filteredAppointments.map((appointment) => (
                  <AppointmentCard
                    appointment={appointment}
                    key={appointment.id}
                    tone="finalizado"
                    onDelete={deleteAppointment}
                    onUpdateStatus={updateStatus}
                    readOnly
                  />
                ))}
              </div>
            )}
          </div>
        ) : statusGroups.map((group) => {
          const items = grouped[group.key];
          return (
            <div className="statusGroup" key={group.key}>
              <header className={`statusGroupHeader ${group.tone}`}>
                <span className={`statusDot ${group.tone}`} />
                <h2>{group.label}</h2>
                <span className="countBadge">{items.length}</span>
              </header>

              {items.length === 0 ? (
                <div className="emptyState">Sem consultas neste status.</div>
              ) : (
                <div className="cardsGrid">
                  {items.map((appointment) => (
                    <AppointmentCard
                      appointment={appointment}
                      key={appointment.id}
                      tone={group.tone}
                      onDelete={deleteAppointment}
                      onUpdateStatus={updateStatus}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </section>

      {isModalOpen ? (
        <div className="modalOverlay" onClick={() => setIsModalOpen(false)}>
          <div className="modalContent" onClick={(event) => event.stopPropagation()}>
            <div className="modalHeader">
              <div>
                <p className="eyebrow">Nova consulta</p>
                <h2>Adicionar paciente</h2>
              </div>
              <button className="iconButton" aria-label="Fechar" onClick={() => setIsModalOpen(false)}>
                <X size={16} />
              </button>
            </div>
            <form onSubmit={createAppointment} className="appointmentForm">
              <input
                required
                placeholder="Nome do paciente"
                value={form.patient_name}
                onChange={(event) => setForm({ ...form, patient_name: event.target.value })}
              />
              <input
                required
                placeholder="Telefone"
                value={form.phone}
                onChange={(event) => setForm({ ...form, phone: formatPhone(event.target.value) })}
                maxLength={15}
              />
              <div className="formRow">
                <input
                  required
                  type="date"
                  value={form.appointment_date}
                  onChange={(event) => setForm({ ...form, appointment_date: event.target.value })}
                />
                <input
                  required
                  type="time"
                  value={form.appointment_time}
                  onChange={(event) => setForm({ ...form, appointment_time: event.target.value })}
                />
              </div>
              <input
                placeholder="Servico (ex: Avaliacao, Limpeza)"
                value={form.service}
                onChange={(event) => setForm({ ...form, service: event.target.value })}
              />
              <button className="primaryButton" type="submit">
                <Plus size={16} />
                Adicionar consulta
              </button>
            </form>
          </div>
        </div>
      ) : null}
    </main>
  );
}

function AppointmentCard({
  appointment,
  tone,
  readOnly = false,
  onDelete,
  onUpdateStatus
}: {
  appointment: Appointment;
  tone: string;
  readOnly?: boolean;
  onDelete: (id: number) => Promise<void>;
  onUpdateStatus: (appointment: Appointment, status: Appointment["status"]) => Promise<void>;
}) {
  return (
    <article className={`appointmentCard ${tone}`} key={appointment.id}>
      <div className="cardTop">
        <strong>{appointment.patient_name}</strong>
        <div className="rowActions">
          {!readOnly && appointment.status !== "Confirmado" ? (
            <button aria-label="Confirmar" onClick={() => onUpdateStatus(appointment, "Confirmado")}>
              <CheckCircle2 size={14} />
            </button>
          ) : null}
          {!readOnly && appointment.status !== "Cancelado" ? (
            <button aria-label="Cancelar" onClick={() => onUpdateStatus(appointment, "Cancelado")}>
              <XCircle size={14} />
            </button>
          ) : null}
          <button aria-label="Excluir" onClick={() => onDelete(appointment.id)}>
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      <div className="cardMeta">
        <CalendarClock size={14} />
        <span>
          {formatDate(appointment.appointment_date)}
          {appointment.appointment_time ? ` · ${appointment.appointment_time.slice(0, 5)}` : ""}
        </span>
      </div>
      {appointment.finalized_at ? (
        <div className="cardMeta mutedMeta">
          <span>Finalizada em {formatDateTime(appointment.finalized_at)}</span>
        </div>
      ) : null}
      {appointment.service ? <span className="serviceTag">{appointment.service}</span> : null}
    </article>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value));
}

function formatPhone(value: string) {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 2) return digits;
  if (digits.length <= 6) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  if (digits.length <= 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}
