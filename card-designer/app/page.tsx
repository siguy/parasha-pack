import Link from 'next/link';
import { listDecks } from '@/lib/api';

// Lists every deck synced into content/ (run ../sync-deck.sh <id> to add one)
export const dynamic = 'force-dynamic';

export default async function Home() {
  const decks = await listDecks();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-slate-800">
      <h1 className="text-4xl font-bold mb-8">Parasha Card Designer</h1>
      {decks.length === 0 && <p>No decks yet. Run ./sync-deck.sh &lt;deck-id&gt; from the repo root.</p>}
      <div className="grid gap-4">
        {decks.map((id) => (
          <Link
            key={id}
            href={`/${id}`}
            className="px-8 py-4 bg-purple-700 text-white rounded-xl shadow-lg hover:bg-purple-800 transition font-bold text-xl capitalize text-center"
          >
            {id}
          </Link>
        ))}
      </div>
    </div>
  );
}
