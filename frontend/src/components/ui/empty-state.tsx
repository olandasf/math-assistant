import { cn } from "@/lib/utils";
import { Button } from "./button";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode | { label: string; onClick: () => void };
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const renderAction = () => {
    if (!action) return null;
    if (
      typeof action === "object" &&
      "label" in action &&
      "onClick" in action
    ) {
      return <Button onClick={action.onClick}>{action.label}</Button>;
    }
    return action;
  };

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 text-center",
        className
      )}
    >
      {icon && <div className="mb-4 text-muted-foreground">{icon}</div>}
      <h3 className="text-lg font-semibold">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-muted-foreground max-w-sm">
          {description}
        </p>
      )}
      {action && <div className="mt-4">{renderAction()}</div>}
    </div>
  );
}
