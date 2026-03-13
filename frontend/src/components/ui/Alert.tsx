/**
 * Alert komponentas - pranešimams ir įspėjimams
 */

import { forwardRef } from "react";
import type { HTMLAttributes, ReactNode } from "react";
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "success" | "error" | "warning" | "info";
  title?: string;
  onDismiss?: () => void;
  icon?: ReactNode;
}

const variantStyles = {
  success: {
    container:
      "bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-200 text-emerald-800",
    icon: "text-emerald-500",
    title: "text-emerald-800",
    dismiss: "hover:bg-emerald-100 text-emerald-500",
  },
  error: {
    container:
      "bg-gradient-to-r from-red-50 to-rose-50 border-red-200 text-red-800",
    icon: "text-red-500",
    title: "text-red-800",
    dismiss: "hover:bg-red-100 text-red-500",
  },
  warning: {
    container:
      "bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200 text-amber-800",
    icon: "text-amber-500",
    title: "text-amber-800",
    dismiss: "hover:bg-amber-100 text-amber-500",
  },
  info: {
    container:
      "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200 text-blue-800",
    icon: "text-blue-500",
    title: "text-blue-800",
    dismiss: "hover:bg-blue-100 text-blue-500",
  },
};

const defaultIcons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const Alert = forwardRef<HTMLDivElement, AlertProps>(
  (
    { className, variant = "info", title, children, onDismiss, icon, ...props },
    ref
  ) => {
    const styles = variantStyles[variant];
    const IconComponent = defaultIcons[variant];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          "relative flex gap-3 rounded-xl border p-4 shadow-sm",
          styles.container,
          className
        )}
        {...props}
      >
        <div className={cn("shrink-0", styles.icon)}>
          {icon || <IconComponent className="h-5 w-5" />}
        </div>
        <div className="flex-1 min-w-0">
          {title && (
            <h5 className={cn("font-semibold mb-1", styles.title)}>{title}</h5>
          )}
          <div className="text-sm">{children}</div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={cn(
              "shrink-0 rounded-lg p-1 transition-colors",
              styles.dismiss
            )}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }
);
Alert.displayName = "Alert";

export { Alert };
