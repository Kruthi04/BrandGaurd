import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default:     "border-transparent bg-primary text-primary-foreground",
        secondary:   "border-transparent bg-secondary text-secondary-foreground",
        outline:     "text-foreground",
        critical:    "border-transparent bg-red-600 text-white",
        high:        "border-transparent bg-orange-500 text-white",
        medium:      "border-transparent bg-yellow-500 text-white",
        low:         "border-transparent bg-slate-400 text-white",
        success:     "border-transparent bg-green-600 text-white",
        investigating: "border-transparent bg-blue-500 text-white",
        corrected:   "border-transparent bg-green-600 text-white",
        dismissed:   "border-transparent bg-slate-400 text-white",
        open:        "border-transparent bg-red-500 text-white",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge };
