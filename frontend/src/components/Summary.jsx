import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Summary() {
    const [stats, setStats] = useState(null)

    useEffect(() => {
        axios.get('http://127.0.0.1:8000/api/stats/summary')
            .then(r => setStats(r.data))
    }, [])

    const cards = [
        { label: 'Total Jobs', value: stats?.total_jobs?.toLocaleString() },
        { label: 'Companies', value: stats?.total_companies?.toLocaleString() },
        { label: 'Unique Skills', value: stats?.total_skills?.toLocaleString() },
        { label: 'Countries', value: stats?.total_countries?.toLocaleString() },
    ]

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map(card => (
                <div key={card.label} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                    <p className="text-gray-400 text-sm">{card.label}</p>
                    <p className="text-2xl font-bold text-white mt-1">
                        {stats ? card.value : '...'}
                    </p>
                </div>
            ))}
        </div>
    )
}