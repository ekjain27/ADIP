import { normalizeRoutePath, toHashRoute } from "./application-shell/navigation.js";

export function getPreviewRoutePath(pathname: string, hash: string): string {
  if (hash.trim()) return normalizeRoutePath(hash);
  return normalizeRoutePath(pathname);
}

export function getPreviewNavigationHash(href: string | null): string {
  return toHashRoute(href ?? "/");
}
