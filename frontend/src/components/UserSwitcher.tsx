import { USERS, type DemoUserId } from "../types";

interface UserSwitcherProps {
  activeUserId: DemoUserId;
  onChange: (userId: DemoUserId) => void;
}

export function UserSwitcher({ activeUserId, onChange }: UserSwitcherProps) {
  return (
    <div className="flex shrink-0 rounded-lg border border-line bg-panel p-1">
      {(Object.keys(USERS) as DemoUserId[]).map((userId) => {
        const user = USERS[userId];
        const selected = userId === activeUserId;
        return (
          <button
            key={userId}
            type="button"
            onClick={() => onChange(userId)}
            className={`w-40 rounded-md px-3 py-2 text-left text-sm ${
              selected
                ? "bg-accent text-white"
                : "text-ink hover:bg-paper"
            }`}
            aria-pressed={selected}
          >
            <span className="block font-semibold">{user.name}</span>
            <span className={`block text-xs ${selected ? "text-white/80" : "text-ink/60"}`}>
              {user.role}
            </span>
          </button>
        );
      })}
    </div>
  );
}
