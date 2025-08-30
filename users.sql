DELETE FROM users;
DELETE FROM sqlite_sequence WHERE name='users';

INSERT INTO users (FullName, Email, Status, Role, Action) VALUES
('Ayesha Khan', 'ayesha@example.com', 'Active', 'Member', 'Edit/Delete'),
('Sara Ali', 'sara@example.com', 'Active', 'Member', 'Edit/Delete'),
('Hina Iqbal', 'hina@example.com', 'Active', 'Member', 'Edit/Delete'),
('Fatima Noor', 'fatima@example.com', 'Active', 'Member', 'Edit/Delete'),
('Zara Malik', 'zara@example.com', 'Active', 'Member', 'Edit/Delete'),
('Maryam Shah', 'maryam@example.com', 'Active', 'Member', 'Edit/Delete'),
('Amna Riaz', 'amna@example.com', 'Active', 'Member', 'Edit/Delete'),
('Rabia Saeed', 'rabia@example.com', 'Active', 'Member', 'Edit/Delete'),
('Sadia Tariq', 'sadia@example.com', 'Active', 'Member', 'Edit/Delete'),
('Nadia Javed', 'nadia@example.com', 'Active', 'Member', 'Edit/Delete'),
('Hira Khan', 'hira@example.com', 'Active', 'Member', 'Edit/Delete'),
('Iqra Bashir', 'iqra@example.com', 'Active', 'Member', 'Edit/Delete'),
('Mahnoor Asif', 'mahnoor@example.com', 'Active', 'Member', 'Edit/Delete'),
('Kainat Rafiq', 'kainat@example.com', 'Active', 'Member', 'Edit/Delete'),
('Sania Nadeem', 'sania@example.com', 'Active', 'Member', 'Edit/Delete');
