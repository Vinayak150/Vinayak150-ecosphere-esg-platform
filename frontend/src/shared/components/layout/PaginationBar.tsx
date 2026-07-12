import { Button } from "@/shared/components/ui/button";

interface PaginationBarProps {
  page: number;
  pages: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function PaginationBar({ page, pages, total, onPageChange }: PaginationBarProps) {
  const safePages = pages || 1;

  return (
    <div className="flex flex-col gap-3 border-t bg-muted/30 px-4 py-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <span>
        Page {page} of {safePages} · {total} total
      </span>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="Previous page"
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= safePages}
          onClick={() => onPageChange(page + 1)}
          aria-label="Next page"
        >
          Next
        </Button>
      </div>
    </div>
  );
}
