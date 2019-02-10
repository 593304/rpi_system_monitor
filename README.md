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
