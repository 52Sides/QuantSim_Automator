export default function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 shadow-sm text-center">
      <p className="text-gray-600 dark:text-gray-300 text-sm">{label}</p>
      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{value}</p>
    </div>
  )
}
