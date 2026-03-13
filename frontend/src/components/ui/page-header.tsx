import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  children,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && <p className="text-muted-foreground">{description}</p>}
      </div>
      {(children || actions) && (
        <div className="flex items-center gap-2">{children || actions}</div>
      )}
    </div>
  );
}
