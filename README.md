# Raspberry Pi System Monitor

Simple python script for saving system values to database for future use

Database schema for the script:

CREATE TABLE monitoring.rpi_data (  
	id BIGSERIAL PRIMARY KEY,  
	cpu_temp_celsius NUMERIC(5, 2),  
	cpu0_usage_percent NUMERIC(5, 2),  
	cpu1_usage_percent NUMERIC(5, 2),  
	cpu2_usage_percent NUMERIC(5, 2),  
	cpu3_usage_percent NUMERIC(5, 2),  
	mem_usage_mb NUMERIC(6, 2),  
	mem_total_mb NUMERIC(6, 2),  
	disk_usage_gb NUMERIC(6, 2),  
	disk_total_gb NUMERIC(6, 2),  
	nas_usage_gb NUMERIC(6, 2),  
	nas_total_gb NUMERIC(6, 2),  
	dev_usage_gb NUMERIC(6, 2),  
	dev_total_gb NUMERIC(6, 2),  
	cloud_usage_gb NUMERIC(6, 2),  
	cloud_total_gb NUMERIC(6, 2),  
	timestamp TIMESTAMP  
)

## Update 1

Views for daily and hourly statistics for CPU and memory

CREATE VIEW monitoring.rpi_data_cpu_mem_hourly AS  
	SELECT  
		ROUND(AVG(cpu_temp_celsius), 2) AS cpu_temp_celsius,  
		ROUND(AVG(cpu0_usage_percent), 2) AS cpu0_usage_percent,  
		ROUND(AVG(cpu1_usage_percent), 2) AS cpu1_usage_percent,  
		ROUND(AVG(cpu2_usage_percent), 2) AS cpu2_usage_percent,  
		ROUND(AVG(cpu3_usage_percent), 2) AS cpu3_usage_percent,  
		ROUND(AVG(mem_usage_mb), 2) AS mem_usage_mb,  
		ROUND(AVG(mem_total_mb), 2) AS mem_total_mb,  
		DATE_TRUNC('hour', timestamp) AS hour  
	FROM  
		monitoring.rpi_data  
	GROUP BY  
		hour  
	ORDER BY  
	hour ASC;

CREATE VIEW monitoring.rpi_data_cpu_mem_daily AS  
	SELECT  
		ROUND(AVG(cpu_temp_celsius), 2) AS cpu_temp_celsius,  
		ROUND(AVG(cpu0_usage_percent), 2) AS cpu0_usage_percent,  
		ROUND(AVG(cpu1_usage_percent), 2) AS cpu1_usage_percent,  
		ROUND(AVG(cpu2_usage_percent), 2) AS cpu2_usage_percent,  
		ROUND(AVG(cpu3_usage_percent), 2) AS cpu3_usage_percent,  
		ROUND(AVG(mem_usage_mb), 2) AS mem_usage_mb,  
		ROUND(AVG(mem_total_mb), 2) AS mem_total_mb,  
		DATE_TRUNC('day', timestamp) AS day  
	FROM  
		monitoring.rpi_data  
	GROUP BY  
		day  
	ORDER BY  
	day ASC;

