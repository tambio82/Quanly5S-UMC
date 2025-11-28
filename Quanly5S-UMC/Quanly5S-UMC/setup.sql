-- =====================================================
-- HỆ THỐNG QUẢN LÝ 5S - UMC
-- Database Schema Setup Script
-- =====================================================

-- 1. Bảng Departments (Khoa/Phòng/Đơn vị)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    unit_code VARCHAR(20) UNIQUE NOT NULL,
    unit_name VARCHAR(200) NOT NULL,
    locations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE departments IS 'Lưu thông tin các khoa/phòng/đơn vị';
COMMENT ON COLUMN departments.unit_code IS 'Mã đơn vị (VD: K01, P02)';
COMMENT ON COLUMN departments.unit_name IS 'Tên đầy đủ đơn vị';
COMMENT ON COLUMN departments.locations IS 'Danh sách vị trí địa lý (JSON array)';

-- 2. Bảng Staff (Nhân sự)
CREATE TABLE IF NOT EXISTS staff (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    staff_code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200),
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE staff IS 'Lưu thông tin nhân sự phụ trách 5S';
COMMENT ON COLUMN staff.role IS 'Vai trò: Thành viên tổ 5S, Điều phối chính';

-- 3. Bảng Areas (Khu vực 5S)
CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(200) NOT NULL,
    area_code VARCHAR(20) NOT NULL,
    definition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE areas IS 'Danh mục các khu vực 5S (VD: Hành chính, Y tế, Kỹ thuật)';

-- 4. Bảng Criteria (Tiêu chí/Hạng mục kiểm tra)
CREATE TABLE IF NOT EXISTS criteria (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id) ON DELETE CASCADE,
    location_name VARCHAR(200),
    category VARCHAR(500),
    requirement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE criteria IS 'Các tiêu chí đánh giá 5S cho từng khu vực';
COMMENT ON COLUMN criteria.location_name IS 'Tên vị trí cụ thể cần kiểm tra';
COMMENT ON COLUMN criteria.category IS 'Hạng mục đánh giá';
COMMENT ON COLUMN criteria.requirement IS 'Yêu cầu chi tiết';

-- 5. Bảng Evaluations (Phiên đánh giá)
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    eval_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE evaluations IS 'Lưu thông tin các phiên đánh giá 5S';

-- 6. Bảng Evaluation Details (Chi tiết đánh giá)
CREATE TABLE IF NOT EXISTS evaluation_details (
    id SERIAL PRIMARY KEY,
    evaluation_id INTEGER REFERENCES evaluations(id) ON DELETE CASCADE,
    criteria_id INTEGER REFERENCES criteria(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    is_pass BOOLEAN DEFAULT FALSE,
    staff_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE evaluation_details IS 'Chi tiết kết quả đánh giá từng hạng mục';
COMMENT ON COLUMN evaluation_details.quantity IS 'Số lượng phát hiện (nếu có)';
COMMENT ON COLUMN evaluation_details.is_pass IS 'True = Đạt, False = Không đạt';

-- =====================================================
-- Indexes để tối ưu hiệu năng
-- =====================================================

CREATE INDEX idx_staff_dept ON staff(department_id);
CREATE INDEX idx_criteria_area ON criteria(area_id);
CREATE INDEX idx_eval_dept_date ON evaluations(department_id, eval_date);
CREATE INDEX idx_eval_details_eval ON evaluation_details(evaluation_id);
CREATE INDEX idx_eval_details_crit ON evaluation_details(criteria_id);

-- =====================================================
-- Sample Data (Optional - Xóa nếu không cần)
-- =====================================================

-- Thêm khu vực mẫu
INSERT INTO areas (area_name, area_code, definition) VALUES
('Khu vực Hành chính', 'HC', 'Văn phòng, phòng họp, khu vực làm việc hành chính'),
('Khu vực Y tế', 'YT', 'Phòng khám, khu điều trị, phòng bệnh'),
('Khu vực Kỹ thuật', 'KT', 'Phòng máy, kho vật tư, khu vực bảo trì')
ON CONFLICT DO NOTHING;

-- Thông báo hoàn thành
DO $$ 
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Tables: departments, staff, areas, criteria, evaluations, evaluation_details';
END $$;
