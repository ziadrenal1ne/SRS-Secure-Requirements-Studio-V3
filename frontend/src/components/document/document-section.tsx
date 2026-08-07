"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { getSectionIcon } from "./icon-map";
import { RequirementBlock } from "./requirement-block";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import type { DocumentSection as DocumentSectionType } from "@/lib/types";

function DocumentSection({
  section,
  open,
  onToggle,
  sectionRef,
}: {
  section: DocumentSectionType;
  open: boolean;
  onToggle: () => void;
  sectionRef: (el: HTMLDivElement | null) => void;
}) {
  const Icon = getSectionIcon(section.icon);

  return (
    <div id={section.id} ref={sectionRef} className="scroll-mt-24 rounded-2xl border border-border bg-surface">
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-3.5 rounded-2xl px-5 py-4 text-left transition-colors hover:bg-surface-2/60 sm:px-6 sm:py-5"
      >
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary">
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-base font-semibold sm:text-lg">{section.title}</h3>
        </div>
        <ChevronDown className={`h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-300 ${open ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="border-t border-border px-5 pb-6 pt-5 sm:px-6">
              <p className="text-sm leading-relaxed text-muted-foreground">{section.summary}</p>

              {section.paragraphs && (
                <div className="mt-4 flex flex-col gap-3">
                  {section.paragraphs.map((p, i) => (
                    <p key={i} className="text-sm leading-relaxed text-foreground">{p}</p>
                  ))}
                </div>
              )}

              {section.requirements && (
                <div className="mt-4 flex flex-col gap-2.5">
                  {section.requirements.map((req) => (
                    <RequirementBlock key={req.id} requirement={req} />
                  ))}
                </div>
              )}

              {section.table && (
                <div className="mt-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {section.table.headers.map((h) => (
                          <TableHead key={h}>{h}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {section.table.rows.map((row, i) => (
                        <TableRow key={i}>
                          {row.map((cell, j) => (
                            <TableCell key={j} className={j === 0 ? "font-medium" : "text-muted-foreground"}>{cell}</TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export { DocumentSection };
