import clsx from "clsx";
import { ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

const baseStyles =
  "flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 text-sm font-bold leading-normal tracking-[0.015em] transition-colors";

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-cta-blue text-background-dark hover:bg-cta-blue/90",
  secondary: "bg-brand-deep text-white hover:bg-brand-deep/90"
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", children, ...rest }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(baseStyles, variantStyles[variant], className)}
        {...rest}
      >
        <span className="truncate">{children}</span>
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
