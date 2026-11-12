const LABELS = {
    draft: "Draft: pending scholarly review",
    reviewed: "Reviewed",
    approved: "Approved",
};

/**
 * Small label showing a lesson's review status.
 * @param {{ status: string }} props
 */
export default function ReviewBadge({ status }) {
    return (
        <span className="inline-block rounded-full border border-current px-3 py-1 text-xs">
            {LABELS[status] ?? status}
        </span>
    );
}