import { useEffect, useState } from 'react'
import axios from 'axios'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer
} from 'recharts'

export default function SkillDemand() {
    const [data, setData] = useState([])

    useEffect(() => {
        axios.get(`${import.meta.env.VITE_API_URL}/api/skills/demand`)
            .then(r => setData(r.data))
    }, [])

    return (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-6">Top 20 Most Demanded Skills</h2>
            <ResponsiveContainer width="100%" height={500}>
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ left: 180, right: 30 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9ca3af" />
                    <YAxis
                        type="category"
                        dataKey="skill_name"
                        stroke="#9ca3af"
                        width={170}
                        tick={{ fontSize: 12 }}
                        tickFormatter={(val) => val.length > 25 ? val.substring(0, 25) + '...' : val}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
                        formatter={(val) => [val.toLocaleString(), 'Job Postings']}
                    />
                    <Bar dataKey="job_count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}