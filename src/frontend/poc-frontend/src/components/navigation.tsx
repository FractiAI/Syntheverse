'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, FileSearch, List, Database, Network, Award, Trophy } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/explorer', label: 'Explorer', icon: FileSearch },
  { href: '/submission', label: 'Submission', icon: List },
  { href: '/tiers', label: 'Tiers', icon: Award },
  { href: '/recognition', label: 'Recognition', icon: Trophy },
  { href: '/registry', label: 'Registry', icon: Database },
  { href: '/sandbox-map', label: 'Sandbox Map', icon: Network },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="border-b bg-card">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-semibold">Syntheverse PoC</span>
          </div>
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || (item.href !== '/sandbox-map' && pathname?.startsWith(item.href + '/'))
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
