# Raspberry Pi System Monitor

Simple python script for saving system values to database for future use

Database schema for the script:
```SQL
CREATE TABLE monitoring.rpi_data (  
    id BIGSERIAL PRIMARY KEY,  
    cpu_temp_celsius NUMERIC(5, 2),  
    cpu0_usage_percent NUMERIC(5, 2),  
    cpu1_usage_percent NUMERIC(5, 2),  
    cpu2_usage_percent NUMERIC(5, 2),  
    cpu3_usage_percent NUMERIC(5, 2),  
    mem_usage_mb NUMERIC(6, 2),  
    mem_total_mb NUMERIC(6, 2),  
    sd_card_usage_gb NUMERIC(6, 2),  
    sd_card_total_gb NUMERIC(6, 2),  
    nas_usage_gb NUMERIC(6, 2),  
    nas_total_gb NUMERIC(6, 2),  
    dev_usage_gb NUMERIC(6, 2),  
    dev_total_gb NUMERIC(6, 2),  
    cloud_usage_gb NUMERIC(6, 2),  
    cloud_total_gb NUMERIC(6, 2),  
    timestamp TIMESTAMP  
)
```

## Update 1

View for hourly average cpu and memory statistics
```SQL
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
```

View for daily average cpu and memory statistics
```SQL
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
```

## Update 2

View for calculating the disk usage difference minute by minute
```SQL
CREATE VIEW monitoring.rpi_data_disk_diff_by_minutes AS  
    SELECT  
        (next.sd_card_usage_gb - base.sd_card_usage_gb) AS sd_card_usage_diff_gb,  
        (next.nas_usage_gb - base.nas_usage_gb) AS nas_usage_diff_gb,  
        (next.dev_usage_gb - base.dev_usage_gb) AS dev_usage_diff_gb,  
        (next.cloud_usage_gb - base.cloud_usage_gb) AS cloud_usage_diff_gb,  
        next.minute  
    FROM  
        (SELECT sd_card_usage_gb, nas_usage_gb, dev_usage_gb, cloud_usage_gb, DATE_TRUNC('minute', timestamp) AS minute FROM monitoring.rpi_data WHERE id < (SELECT MAX(id) FROM monitoring.rpi_data) ORDER BY minute) AS base,  
        (SELECT sd_card_usage_gb, nas_usage_gb, dev_usage_gb, cloud_usage_gb, DATE_TRUNC('minute', timestamp) AS minute FROM monitoring.rpi_data WHERE id > (SELECT MIN(id) FROM monitoring.rpi_data) ORDER BY minute) AS next  
    WHERE  
        (base.minute + (interval '1 minute')) = next.minute  
    ORDER BY  
        next.minute ASC;
```

View for disk usage differences by hours
```SQL
CREATE VIEW monitoring.rpi_data_disk_diff_by_hours AS  
    SELECT  
        SUM(sd_card_usage_diff_gb) AS sd_card_usage_diff_gb,  
        SUM(nas_usage_diff_gb) AS nas_usage_diff_gb,  
        SUM(dev_usage_diff_gb) AS dev_usage_diff_gb,  
        SUM(cloud_usage_diff_gb) AS cloud_usage_diff_gb,   
        DATE_TRUNC('hour', minute) AS hour  
    FROM  
        monitoring.rpi_data_disk_diff_by_minutes  
    GROUP BY  
        hour  
    ORDER BY  
        hour ASC;
```

View for disk usage differences by days
```SQL
CREATE VIEW monitoring.rpi_data_disk_diff_by_days AS  
    SELECT  
        SUM(sd_card_usage_diff_gb) AS sd_card_usage_diff_gb,  
        SUM(nas_usage_diff_gb) AS nas_usage_diff_gb,  
        SUM(dev_usage_diff_gb) AS dev_usage_diff_gb,  
        SUM(cloud_usage_diff_gb) AS cloud_usage_diff_gb,   
        DATE_TRUNC('day', minute) AS day  
    FROM  
        monitoring.rpi_data_disk_diff_by_minutes  
    GROUP BY  
        day  
    ORDER BY  
        day ASC;
```

## Update 3

Values will be saved to a temporary file if cannot connect to the database

## Update 4

Added REST API calls for notifying a custom dashboard application

## Update 5

Added config file

## Update 6

Handling multiple comma separated host address in config file
