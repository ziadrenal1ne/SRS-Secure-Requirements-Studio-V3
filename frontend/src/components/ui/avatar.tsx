import { cn } from "@/lib/utils";

function Avatar({ initials, className, size = "md" }: { initials: string; className?: string; size?: "sm" | "md" | "lg" }) {
  const sizeClasses = { sm: "h-7 w-7 text-[11px]", md: "h-9 w-9 text-xs", lg: "h-12 w-12 text-sm" };
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent font-display font-semibold text-white",
        sizeClasses[size],
        className
      )}
    >
      {initials}
    </div>
  );
}

export { Avatar };
