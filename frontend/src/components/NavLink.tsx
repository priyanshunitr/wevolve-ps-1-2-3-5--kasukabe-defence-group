import Link from "next/link";
import { usePathname } from "next/navigation";
import { forwardRef } from "react";
import { cn } from "@/lib/utils";

type NavLinkCompatProps = React.ComponentProps<typeof Link> & {
  to: string; // Compatibility
  activeClassName?: string;
  pendingClassName?: string;
};

const NavLink = forwardRef<HTMLAnchorElement, NavLinkCompatProps>(
  ({ className, activeClassName, pendingClassName, to, href, ...props }, ref) => {
    const pathname = usePathname();
    const isActive = pathname === to;

    return (
      <Link
        href={to}
        className={cn(className, isActive && activeClassName)}
        {...props}
      >
        {props.children}
      </Link>
    );
  },
);

NavLink.displayName = "NavLink";

export { NavLink };
