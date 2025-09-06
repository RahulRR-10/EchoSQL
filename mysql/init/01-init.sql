-- Create Tables

-- Teams Table
CREATE TABLE IF NOT EXISTS teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_short_name VARCHAR(10) NOT NULL,
    city VARCHAR(50),
    home_ground VARCHAR(100),
    owner VARCHAR(100),
    founded_year INT,
    total_titles INT DEFAULT 0
);

-- Players Table
CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    date_of_birth DATE,
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    role VARCHAR(50) -- Batsman, Bowler, All-rounder, Wicket-keeper
);

-- Team Players Table (Many-to-Many relationship as players can change teams)
CREATE TABLE IF NOT EXISTS team_players (
    team_player_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    player_id INT,
    season_year INT,
    jersey_number INT,
    is_captain BOOLEAN DEFAULT FALSE,
    base_price_inr DECIMAL(12,2),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Matches Table
CREATE TABLE IF NOT EXISTS matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    season_year INT,
    match_date DATE,
    venue VARCHAR(100),
    home_team_id INT,
    away_team_id INT,
    toss_winner_id INT,
    toss_decision VARCHAR(10), -- Bat or Field
    match_winner_id INT,
    man_of_the_match_player_id INT,
    win_type VARCHAR(20), -- Runs, Wickets, Super Over
    win_margin INT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (toss_winner_id) REFERENCES teams(team_id),
    FOREIGN KEY (match_winner_id) REFERENCES teams(team_id),
    FOREIGN KEY (man_of_the_match_player_id) REFERENCES players(player_id)
);

-- Player Performances Table
CREATE TABLE IF NOT EXISTS player_performances (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    player_id INT,
    team_id INT,
    runs_scored INT DEFAULT 0,
    balls_faced INT DEFAULT 0,
    fours INT DEFAULT 0,
    sixes INT DEFAULT 0,
    overs_bowled DECIMAL(3,1) DEFAULT 0,
    runs_conceded INT DEFAULT 0,
    wickets INT DEFAULT 0,
    catches INT DEFAULT 0,
    stumpings INT DEFAULT 0,
    run_outs INT DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Seasons Table
CREATE TABLE IF NOT EXISTS seasons (
    season_id INT AUTO_INCREMENT PRIMARY KEY,
    year INT UNIQUE,
    start_date DATE,
    end_date DATE,
    winner_team_id INT,
    runner_up_team_id INT,
    total_matches INT,
    most_runs_player_id INT,
    most_wickets_player_id INT,
    FOREIGN KEY (winner_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (runner_up_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (most_runs_player_id) REFERENCES players(player_id),
    FOREIGN KEY (most_wickets_player_id) REFERENCES players(player_id)
);

-- Insert sample data into teams
INSERT INTO teams (team_name, team_short_name, city, home_ground, owner, founded_year, total_titles)
VALUES 
('Mumbai Indians', 'MI', 'Mumbai', 'Wankhede Stadium', 'Reliance Industries', 2008, 5),
('Chennai Super Kings', 'CSK', 'Chennai', 'M. A. Chidambaram Stadium', 'Chennai Super Kings Cricket Ltd.', 2008, 4),
('Royal Challengers Bangalore', 'RCB', 'Bengaluru', 'M. Chinnaswamy Stadium', 'United Spirits', 2008, 0),
('Kolkata Knight Riders', 'KKR', 'Kolkata', 'Eden Gardens', 'Red Chillies Entertainment', 2008, 2),
('Delhi Capitals', 'DC', 'Delhi', 'Arun Jaitley Stadium', 'JSW Group & GMR Group', 2008, 0),
('Rajasthan Royals', 'RR', 'Jaipur', 'Sawai Mansingh Stadium', 'Manoj Badale', 2008, 1),
('Sunrisers Hyderabad', 'SRH', 'Hyderabad', 'Rajiv Gandhi Cricket Stadium', 'SUN Group', 2013, 1),
('Punjab Kings', 'PBKS', 'Mohali', 'IS Bindra Stadium', 'Preity Zinta & Ness Wadia', 2008, 0),
('Gujarat Titans', 'GT', 'Ahmedabad', 'Narendra Modi Stadium', 'CVC Capital Partners', 2022, 1),
('Lucknow Super Giants', 'LSG', 'Lucknow', 'BRSABV Ekana Cricket Stadium', 'RPSG Group', 2022, 0);

-- Insert sample players
INSERT INTO players (player_name, country, date_of_birth, batting_style, bowling_style, role)
VALUES
('Virat Kohli', 'India', '1988-11-05', 'Right-handed', 'Right-arm medium', 'Batsman'),
('Rohit Sharma', 'India', '1987-04-30', 'Right-handed', 'Right-arm off break', 'Batsman'),
('MS Dhoni', 'India', '1981-07-07', 'Right-handed', NULL, 'Wicket-keeper'),
('Jasprit Bumrah', 'India', '1993-12-06', 'Right-handed', 'Right-arm fast', 'Bowler'),
('AB de Villiers', 'South Africa', '1984-02-17', 'Right-handed', 'Right-arm medium', 'Batsman'),
('Chris Gayle', 'West Indies', '1979-09-21', 'Left-handed', 'Right-arm off break', 'Batsman'),
('Ravindra Jadeja', 'India', '1988-12-06', 'Left-handed', 'Left-arm orthodox', 'All-rounder'),
('Andre Russell', 'West Indies', '1988-04-29', 'Right-handed', 'Right-arm fast medium', 'All-rounder'),
('Rashid Khan', 'Afghanistan', '1998-09-20', 'Right-handed', 'Right-arm leg break', 'Bowler'),
('Jos Buttler', 'England', '1990-09-08', 'Right-handed', NULL, 'Wicket-keeper'),
('KL Rahul', 'India', '1992-04-18', 'Right-handed', NULL, 'Wicket-keeper'),
('Hardik Pandya', 'India', '1993-10-11', 'Right-handed', 'Right-arm fast medium', 'All-rounder'),
('Suryakumar Yadav', 'India', '1990-09-14', 'Right-handed', 'Right-arm medium', 'Batsman'),
('Rishabh Pant', 'India', '1997-10-04', 'Left-handed', NULL, 'Wicket-keeper'),
('Yuzvendra Chahal', 'India', '1990-07-23', 'Right-handed', 'Right-arm leg break', 'Bowler');

-- Associate players with teams for the 2023 season
INSERT INTO team_players (team_id, player_id, season_year, jersey_number, is_captain)
VALUES
(3, 1, 2023, 18, TRUE),  -- Virat Kohli at RCB
(1, 2, 2023, 45, TRUE),  -- Rohit Sharma at MI
(2, 3, 2023, 7, TRUE),   -- MS Dhoni at CSK
(1, 4, 2023, 93, FALSE), -- Jasprit Bumrah at MI
(3, 5, 2023, 17, FALSE), -- AB de Villiers at RCB
(3, 6, 2023, 333, FALSE), -- Chris Gayle at RCB
(2, 7, 2023, 8, FALSE),  -- Ravindra Jadeja at CSK
(4, 8, 2023, 12, FALSE), -- Andre Russell at KKR
(7, 9, 2023, 19, FALSE), -- Rashid Khan at SRH
(6, 10, 2023, 63, FALSE), -- Jos Buttler at RR
(8, 11, 2023, 1, TRUE),  -- KL Rahul at PBKS
(9, 12, 2023, 33, TRUE), -- Hardik Pandya at GT
(1, 13, 2023, 63, FALSE), -- Suryakumar Yadav at MI
(5, 14, 2023, 17, TRUE), -- Rishabh Pant at DC
(3, 15, 2023, 3, FALSE); -- Yuzvendra Chahal at RCB

-- Insert sample seasons
INSERT INTO seasons (year, start_date, end_date, winner_team_id, runner_up_team_id, total_matches)
VALUES
(2020, '2020-09-19', '2020-11-10', 1, 5, 60),
(2021, '2021-04-09', '2021-10-15', 2, 4, 60),
(2022, '2022-03-26', '2022-05-29', 9, 6, 74),
(2023, '2023-03-31', '2023-05-28', 2, 9, 74);

-- Insert sample matches from the 2023 season
INSERT INTO matches (season_year, match_date, venue, home_team_id, away_team_id, toss_winner_id, toss_decision, match_winner_id, man_of_the_match_player_id, win_type, win_margin)
VALUES
(2023, '2023-03-31', 'Narendra Modi Stadium', 9, 2, 9, 'Field', 2, 7, 'Wickets', 5),
(2023, '2023-04-01', 'Eden Gardens', 4, 8, 8, 'Bat', 8, 11, 'Runs', 7),
(2023, '2023-04-02', 'M. Chinnaswamy Stadium', 3, 1, 1, 'Bat', 3, 1, 'Runs', 8),
(2023, '2023-04-03', 'Rajiv Gandhi Cricket Stadium', 7, 6, 7, 'Field', 6, 10, 'Wickets', 4),
(2023, '2023-04-04', 'Arun Jaitley Stadium', 5, 10, 5, 'Bat', 5, 14, 'Runs', 12),
(2023, '2023-05-28', 'Narendra Modi Stadium', 2, 9, 2, 'Bat', 2, 3, 'Runs', 5);

-- Insert player performances for a few matches
INSERT INTO player_performances (match_id, player_id, team_id, runs_scored, balls_faced, fours, sixes, overs_bowled, runs_conceded, wickets)
VALUES
-- Match 1: GT vs CSK
(1, 12, 9, 45, 32, 4, 2, 0, 0, 0),  -- Hardik Pandya batting
(1, 3, 2, 32, 28, 3, 1, 0, 0, 0),   -- MS Dhoni batting
(1, 7, 2, 25, 18, 2, 1, 4.0, 28, 3), -- Jadeja bowling and batting

-- Match 3: RCB vs MI
(3, 1, 3, 82, 48, 6, 5, 0, 0, 0),   -- Virat Kohli batting
(3, 2, 1, 48, 36, 4, 2, 0, 0, 0),   -- Rohit Sharma batting
(3, 4, 1, 0, 0, 0, 0, 4.0, 32, 2),  -- Bumrah bowling
(3, 15, 3, 0, 0, 0, 0, 4.0, 26, 3); -- Chahal bowling

-- Create a sales database for the second example
CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

-- Create sales tables
CREATE TABLE IF NOT EXISTS regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS sales_representatives (
    rep_id INT AUTO_INCREMENT PRIMARY KEY,
    rep_name VARCHAR(100) NOT NULL,
    region_id INT,
    hire_date DATE,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    region_id INT,
    segment VARCHAR(50),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATE NOT NULL,
    product_id INT,
    customer_id INT,
    rep_id INT,
    quantity INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (rep_id) REFERENCES sales_representatives(rep_id)
);

-- Insert regions
INSERT INTO regions (region_name) VALUES 
('North'), ('South'), ('East'), ('West'), ('Central');

-- Insert products
INSERT INTO products (product_name, category, unit_price) VALUES
('Laptop Pro', 'Electronics', 1200.00),
('Smartphone X', 'Electronics', 800.00),
('Office Chair', 'Furniture', 120.00),
('Desk Lamp', 'Furniture', 45.00),
('Coffee Maker', 'Appliances', 85.00),
('Blender', 'Appliances', 65.00),
('Wireless Headphones', 'Electronics', 120.00),
('External SSD', 'Electronics', 150.00),
('Ergonomic Keyboard', 'Electronics', 90.00),
('Desk', 'Furniture', 220.00);

-- Insert sales representatives
INSERT INTO sales_representatives (rep_name, region_id, hire_date) VALUES
('John Smith', 1, '2021-01-15'),
('Emma Johnson', 2, '2021-02-20'),
('Michael Brown', 3, '2021-03-10'),
('Sarah Davis', 4, '2021-04-05'),
('Robert Wilson', 5, '2021-05-12'),
('Jennifer Taylor', 1, '2021-06-22'),
('David Anderson', 2, '2021-07-18'),
('Lisa Thomas', 3, '2021-08-30'),
('James Jackson', 4, '2021-09-15'),
('Patricia White', 5, '2021-10-10');

-- Insert customers
INSERT INTO customers (customer_name, region_id, segment) VALUES
('Tech Solutions Inc.', 1, 'Corporate'),
('Home Essentials', 2, 'Consumer'),
('Office Supplies Ltd', 3, 'Corporate'),
('Retail Giants', 4, 'Retail'),
('Digital Services', 5, 'Corporate'),
('Modern Living', 1, 'Consumer'),
('Smart Systems', 2, 'Corporate'),
('Budget Buys', 3, 'Retail'),
('Luxury Lifestyles', 4, 'Consumer'),
('Business Solutions', 5, 'Corporate');

-- Insert sales data for 2023 (Q1 to Q2)
-- January 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-01-05', 1, 1, 1, 10, 12000.00),
('2023-01-10', 2, 2, 2, 15, 12000.00),
('2023-01-15', 3, 3, 3, 20, 2400.00),
('2023-01-20', 4, 4, 4, 25, 1125.00),
('2023-01-25', 5, 5, 5, 30, 2550.00);

-- February 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-02-05', 6, 6, 6, 12, 780.00),
('2023-02-10', 7, 7, 7, 18, 2160.00),
('2023-02-15', 8, 8, 8, 22, 3300.00),
('2023-02-20', 9, 9, 9, 14, 1260.00),
('2023-02-25', 10, 10, 10, 16, 3520.00);

-- March 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-03-05', 1, 10, 1, 8, 9600.00),
('2023-03-10', 2, 9, 2, 13, 10400.00),
('2023-03-15', 3, 8, 3, 17, 2040.00),
('2023-03-20', 4, 7, 4, 24, 1080.00),
('2023-03-25', 5, 6, 5, 19, 1615.00);

-- April 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-04-05', 6, 5, 6, 11, 715.00),
('2023-04-10', 7, 4, 7, 20, 2400.00),
('2023-04-15', 8, 3, 8, 15, 2250.00),
('2023-04-20', 9, 2, 9, 22, 1980.00),
('2023-04-25', 10, 1, 10, 18, 3960.00);

-- May 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-05-05', 1, 2, 1, 9, 10800.00),
('2023-05-10', 2, 3, 2, 14, 11200.00),
('2023-05-15', 3, 4, 3, 21, 2520.00),
('2023-05-20', 4, 5, 4, 26, 1170.00),
('2023-05-25', 5, 6, 5, 32, 2720.00);

-- June 2023
INSERT INTO sales (sale_date, product_id, customer_id, rep_id, quantity, total_amount) VALUES
('2023-06-05', 6, 7, 6, 13, 845.00),
('2023-06-10', 7, 8, 7, 19, 2280.00),
('2023-06-15', 8, 9, 8, 23, 3450.00),
('2023-06-20', 9, 10, 9, 15, 1350.00),
('2023-06-25', 10, 1, 10, 17, 3740.00);

-- Use the main database again
USE echosql_db;
