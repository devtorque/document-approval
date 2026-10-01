interface ErrorBannerProps {
  message: string;
}

export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="h-11">
      {message ? (
        <div
          role="alert"
          className="flex h-full items-center rounded-lg border border-red-200 bg-red-50 px-4 text-sm text-red-800"
        >
          {message}
        </div>
      ) : null}
    </div>
  );
}
