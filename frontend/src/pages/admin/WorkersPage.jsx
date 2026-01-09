import React, { useState, useEffect } from 'react';
import { Table, Group, Text, Button, Modal, TextInput, FileInput, Badge, ActionIcon, Notification } from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { IconEdit, IconUpload, IconBan, IconCheck } from '@tabler/icons-react';
import { workerApi } from '../../services/workerApi';

export default function WorkersPage() {
  const [workers, setWorkers] = useState([]);
  const [opened, setOpened] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Selected worker for editing (null if creating new)
  const [editingId, setEditingId] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    expiration_date: new Date(),
    file: null
  });

  // 1. Fetch Workers on Load
  useEffect(() => {
    loadWorkers();
  }, []);

  const loadWorkers = async () => {
    try {
        const data = await workerApi.getAll();
        // Ensure data is array (backend might return single object if logic fails)
        setWorkers(Array.isArray(data) ? data : []); 
    } catch (err) {
        console.error(err);
        setError("Could not load workers");
    }
  };

  // 2. Open Modal (Reset form or Fill form)
  const handleOpenModal = (worker = null) => {
    setError(null);
    if (worker) {
      setEditingId(worker.id);
      setFormData({
        name: worker.name,
        // Parse the ISO string from backend back to JS Date object
        expiration_date: new Date(worker.expiration_date),
        file: null // We don't preload files for security reasons
      });
    } else {
      setEditingId(null);
      setFormData({ name: '', expiration_date: new Date(), file: null });
    }
    setOpened(true);
  };

  // 3. Submit Form (Create or Update)
  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
        if (editingId) {
            // UPDATE EXISTING
            await workerApi.update(
                editingId, 
                formData.name, 
                formData.expiration_date, 
                formData.file
            );
        } else {
            // CREATE NEW
            // Backend requires file for creation
            if (!formData.file) {
                throw new Error("Face image is required for new workers");
            }
            await workerApi.create(
                formData.name, 
                formData.expiration_date, 
                formData.file
            );
        }
        setOpened(false);
        loadWorkers(); // Refresh list
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  // 4. Invalidate Worker (Revoke Access)
  const handleInvalidate = async (id) => {
    if(!window.confirm("Are you sure you want to revoke access immediately?")) return;
    try {
        await workerApi.invalidate(id);
        loadWorkers();
    } catch (err) {
        alert("Failed to invalidate worker");
    }
  };

  // Helper to check if worker is active
  const isActive = (isoDate) => new Date(isoDate) > new Date();

  return (
    <div>
      <Group position="apart" mb="md">
        <Text size="xl" weight={700}>Worker Management</Text>
        <Button onClick={() => handleOpenModal()}>+ Add Worker</Button>
      </Group>

      {error && <Notification color="red" onClose={() => setError(null)} mb="md">{error}</Notification>}

      <Table striped highlightOnHover withBorder verticalSpacing="sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Expiration</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {workers.map((worker) => (
            <tr key={worker.id}>
              <td>{worker.id}</td>
              <td>{worker.name}</td>
              <td>{new Date(worker.expiration_date).toLocaleDateString()}</td>
              <td>
                {isActive(worker.expiration_date) 
                    ? <Badge color="green" variant="filled">Active</Badge> 
                    : <Badge color="gray" variant="filled">Expired</Badge>}
              </td>
              <td>
                <Group spacing="xs">
                  <ActionIcon onClick={() => handleOpenModal(worker)} color="blue" variant="light" title="Edit">
                    <IconEdit size={18} />
                  </ActionIcon>
                  {isActive(worker.expiration_date) && (
                      <ActionIcon onClick={() => handleInvalidate(worker.id)} color="red" variant="light" title="Revoke Access">
                        <IconBan size={18} />
                      </ActionIcon>
                  )}
                </Group>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      {/* MODAL FORM */}
      <Modal 
        opened={opened} 
        onClose={() => setOpened(false)} 
        title={editingId ? "Edit Worker" : "New Worker"}
      >
        <TextInput
            label="Name"
            placeholder="John Doe"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            mb="sm"
            required
        />
        
        <DatePickerInput
            label="Expiration Date"
            placeholder="Select date"
            value={formData.expiration_date}
            onChange={(date) => setFormData({...formData, expiration_date: date})}
            mb="sm"
            required
        />

        <FileInput
            label={editingId ? "Update Face Image (Optional)" : "Face Image (Required)"}
            placeholder="Upload photo"
            icon={<IconUpload size={14} />}
            value={formData.file}
            onChange={(file) => setFormData({...formData, file: file})}
            mb="lg"
            required={!editingId}
        />

        <Group position="right">
            <Button variant="default" onClick={() => setOpened(false)}>Cancel</Button>
            <Button onClick={handleSubmit} loading={loading}>
                {editingId ? "Save Changes" : "Create Worker"}
            </Button>
        </Group>
      </Modal>
    </div>
  );
}