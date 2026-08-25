import { useEffect, useState } from 'react'
import axios from 'axios'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer
} from 'recharts'

export default function HiringByCountry() {
    const [data, setData] = useState([])

    useEffect(() => {
        axios.get(`${import.meta.env.VITE_API_URL}/api/hiring/by-country?limit=15`)
            .then(r => setData(r.data))
    }, [])

    return (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-6">Top Countries by Job Postings</h2>
            <ResponsiveContainer width="100%" height={500}>
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ left: 140, right: 30 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9ca3af" />
                    <YAxis
                        type="category"
                        dataKey="country"
                        stroke="#9ca3af"
                        width={130}
                        tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
                        formatter={(val) => [val.toLocaleString(), 'Job Postings']}
                    />
                    <Bar dataKey="job_count" fill="#f59e0b" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}