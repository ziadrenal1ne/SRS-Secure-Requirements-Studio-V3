"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface RadioProps {
  checked: boolean;
  onSelect: () => void;
  className?: string;
}

function Radio({ checked, onSelect, className }: RadioProps) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={checked}
      onClick={onSelect}
      className={cn(
        "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors duration-150",
        checked ? "border-primary" : "border-border-strong hover:border-primary",
        className
      )}
    >
      {checked && <span className="h-2.5 w-2.5 rounded-full bg-primary" />}
    </button>
  );
}

export { Radio };
