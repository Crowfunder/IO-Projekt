import React from 'react';
import { AppShell, Text, Group, NavLink, ActionIcon, useMantineTheme, Burger } from '@mantine/core';
import { IconUsers, IconLogout, IconShieldLock } from '@tabler/icons-react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useMantineTheme();
  // Toggle for mobile responsiveness
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      {/* 1. Header Section */}
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <IconShieldLock size={30} color={theme.colors.blue[6]} />
            <Text fw={700} size="lg">SecureEntry Admin</Text>
          </Group>
          <ActionIcon variant="light" color="red" title="Logout">
            <IconLogout size={20} />
          </ActionIcon>
        </Group>
      </AppShell.Header>

      {/* 2. Sidebar Section */}
      <AppShell.Navbar p="md">
        <NavLink 
            label="Workers Management" 
            leftSection={<IconUsers size={16} />} 
            active={location.pathname === '/admin/workers'}
            onClick={() => {
                navigate('/admin/workers');
                toggle(); // Close menu on mobile after click
            }} 
        />
      </AppShell.Navbar>

      {/* 3. Main Content Area */}
      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}