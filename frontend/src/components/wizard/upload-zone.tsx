"use client";

import * as React from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

function UploadZone({
  fileName,
  onChange,
  className,
}: {
  fileName: string | null;
  onChange: (fileName: string | null) => void;
  className?: string;
}) {
  const [dragging, setDragging] = React.useState(false);

  function simulateDrop() {
    onChange("schema-architecture-pgb.pdf");
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); simulateDrop(); }}
      className={cn(
        "flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 text-center transition-colors",
        dragging ? "border-primary bg-primary-soft" : "border-border-strong bg-surface-2",
        className
      )}
    >
      {fileName ? (
        <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
          <FileText className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">{fileName}</span>
          <button onClick={() => onChange(null)} className="rounded-full p-1 hover:bg-surface-2">
            <X className="h-3.5 w-3.5 text-muted-foreground" />
          </button>
        </div>
      ) : (
        <>
          <UploadCloud className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm font-medium">Glissez-déposez un fichier ici</p>
          <p className="text-xs text-muted-foreground">PDF, PNG ou JPG jusqu&apos;à 10 Mo</p>
          <button onClick={simulateDrop} type="button" className="mt-1 text-xs font-medium text-primary hover:underline">
            ou parcourir vos fichiers
          </button>
        </>
      )}
    </div>
  );
}

export { UploadZone };
