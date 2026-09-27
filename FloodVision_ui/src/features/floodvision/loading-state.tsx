import { CloudRain, LocateFixed, Waves } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingState({ stage }: { stage: number }) {
  const steps = [{ icon: LocateFixed, label: "Finding location" }, { icon: CloudRain, label: "Getting current weather" }, { icon: Waves, label: "Checking flood risk" }];
  return <section className="mx-auto max-w-4xl py-14" aria-live="polite"><div className="rounded-lg border border-border bg-card p-6 shadow-card sm:p-8"><div className="grid gap-4 sm:grid-cols-3">{steps.map((step, index) => { const Icon = step.icon; const active = index <= stage; return <div key={step.label} className={`flex items-center gap-3 rounded-md p-4 ${active ? "bg-brand-soft text-brand" : "bg-surface-strong text-muted-foreground"}`}><Icon className={index === stage ? "animate-pulse" : ""} /><span className="text-sm font-semibold">{step.label}{index === stage ? "…" : ""}</span></div>; })}</div><div className="mt-8 grid gap-4 sm:grid-cols-2"><Skeleton className="h-44" /><Skeleton className="h-44" /></div></div></section>;
}