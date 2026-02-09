
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
      <h1 className="text-4xl font-bold mb-8 text-slate-800">Parasha Card Designer</h1>
      <div className="grid gap-4">
        <Link 
          href="/terumah"
          className="px-8 py-4 bg-purple-600 text-white rounded-xl shadow-lg hover:bg-purple-700 transition font-bold text-xl"
        >
          Open Terumah Deck
        </Link>
      </div>
    </div>
  );
}
