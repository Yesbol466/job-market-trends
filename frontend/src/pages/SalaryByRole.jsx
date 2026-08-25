import { useEffect, useState } from 'react'
import axios from 'axios'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer
} from 'recharts'

export default function SalaryByRole() {
    const [data, setData] = useState([])

    useEffect(() => {
        axios.get(`${import.meta.env.VITE_API_URL}/api/salary/by-role?limit=15`)
            .then(r => setData(r.data))
    }, [])

    return (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-6">Average Salary by Role</h2>
            <ResponsiveContainer width="100%" height={500}>
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ left: 220, right: 30 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9ca3af"
                        tickFormatter={v => `$${(v / 1000).toFixed(0)}K`}
                    />
                    <YAxis
                        type="category"
                        dataKey="role"
                        stroke="#9ca3af"
                        width={210}
                        tick={{ fontSize: 11 }}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
                        formatter={(val) => [`$${val.toLocaleString()}`, 'Avg Salary']}
                    />
                    <Bar dataKey="avg_salary" fill="#10b981" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}