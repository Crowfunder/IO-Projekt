import React from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import EntryTerminal from './pages/EntryTerminal';
import AdminLayout from './pages/admin/AdminLayout'; 
import WorkersPage from './pages/admin/WorkersPage'; 

function App() {
  return (
    <MantineProvider withGlobalStyles withNormalizeCSS theme={{ colorScheme: 'dark' }}>
      <BrowserRouter>
        <Routes>
            {/* Public/Terminal Route */}
            <Route path="/" element={<EntryTerminal />} />
            
            {/* Admin Routes */}
            <Route path="/admin" element={<AdminLayout />}>
                {/* Redirect /admin to /admin/workers automatically */}
                <Route index element={<Navigate to="/admin/workers" replace />} />
                <Route path="workers" element={<WorkersPage />} />
            </Route>
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  );
}

export default App;