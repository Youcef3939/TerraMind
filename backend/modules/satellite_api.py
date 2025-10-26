import requests
import asyncio
import aiohttp # type: ignore
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import os
import numpy as np
from dataclasses import dataclass

@dataclass
class SatelliteImage:
    url: str
    date: datetime
    satellite: str
    resolution: float
    cloud_coverage: float

class SatelliteAPI:
    
    def __init__(self, sentinel_hub_key: str = None, landsat_key: str = None): # type: ignore
        self.sentinel_hub_key = sentinel_hub_key or "demo_key"
        self.landsat_key = landsat_key or "demo_key"
        
        self.sentinel_hub_url = "https://services.sentinel-hub.com/api/v1"
        self.landsat_url = "https://api.landsatlook.usgs.gov"
        
        self.demo_images = self._load_demo_images()
    
    async def get_recent_image(self, lat: float, lon: float, radius_km: float) -> str:
        try:
            image = await self._get_sentinel_image(lat, lon, radius_km, recent=True)
            if image:
                return image.url
            
            image = await self._get_landsat_image(lat, lon, radius_km, recent=True)
            if image:
                return image.url
            
            return self._get_demo_image_url(lat, lon, "recent")
            
        except Exception as e:
            print(f"Error getting recent image: {e}")
            return self._get_demo_image_url(lat, lon, "recent")
    
    async def get_historical_image(self, lat: float, lon: float, radius_km: float, target_date: datetime) -> str:

        try:
            image = await self._get_sentinel_image(lat, lon, radius_km, target_date=target_date)
            if image:
                return image.url
            
            image = await self._get_landsat_image(lat, lon, radius_km, target_date=target_date)
            if image:
                return image.url
            
            return self._get_demo_image_url(lat, lon, "historical")
            
        except Exception as e:
            print(f"Error getting historical image: {e}")
            return self._get_demo_image_url(lat, lon, "historical")
    
    async def get_image(self, lat: float, lon: float, radius_km: float, target_date: Optional[datetime] = None) -> str:

        if target_date:
            return await self.get_historical_image(lat, lon, radius_km, target_date)
        else:
            return await self.get_recent_image(lat, lon, radius_km)
    
    async def _get_sentinel_image(self, lat: float, lon: float, radius_km: float, 
                                 recent: bool = True, target_date: Optional[datetime] = None) -> Optional[SatelliteImage]:

        if self.sentinel_hub_key == "demo_key":
            return None
        
        try:
            bbox = self._calculate_bbox(lat, lon, radius_km)
            
            if recent:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
                end_date = datetime.now().isoformat()
            else:
                start_date = (target_date - timedelta(days=7)).isoformat() # type: ignore
                end_date = (target_date + timedelta(days=7)).isoformat() # type: ignore
            
            payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [
                        {
                            "type": "sentinel-2-l2a",
                            "dataFilter": {
                                "timeRange": {
                                    "from": start_date,
                                    "to": end_date
                                },
                                "maxCloudCoverage": 20
                            }
                        }
                    ]
                },
                "output": {
                    "width": 512,
                    "height": 512,
                    "responses": [
                        {
                            "identifier": "default",
                            "format": {
                                "type": "image/jpeg"
                            }
                        }
                    ]
                },
                "evalscript": """
                //VERSION=3
                function setup() {
                    return {
                        input: ["B02", "B03", "B04", "B08"],
                        output: { bands: 4 }
                    };
                }
                function evaluatePixel(sample) {
                    return [sample.B04, sample.B03, sample.B02, sample.B08];
                }
                """
            }
            
            headers = {
                "Authorization": f"Bearer {self.sentinel_hub_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.sentinel_hub_url}/process",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        image_url = f"https://demo-sentinel-image-{lat}-{lon}.jpg"
                        return SatelliteImage(
                            url=image_url,
                            date=target_date or datetime.now(),
                            satellite="Sentinel-2",
                            resolution=10.0,
                            cloud_coverage=5.0
                        )
                    else:
                        return None
                        
        except Exception as e:
            print(f"Sentinel Hub API error: {e}")
            return None
    
    async def _get_landsat_image(self, lat: float, lon: float, radius_km: float,
                                recent: bool = True, target_date: Optional[datetime] = None) -> Optional[SatelliteImage]:

        if self.landsat_key == "demo_key":
            return None
        
        try:
            bbox = self._calculate_bbox(lat, lon, radius_km)
            
            if recent:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            else:
                start_date = (target_date - timedelta(days=7)).strftime("%Y-%m-%d") # type: ignore
                end_date = (target_date + timedelta(days=7)).strftime("%Y-%m-%d") # type: ignore
            
            params = {
                "lat": lat,
                "lon": lon,
                "start_date": start_date,
                "end_date": end_date,
                "max_cloud_cover": 20
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.landsat_url}/satellite-search",
                    params=params,
                    headers={"Authorization": f"Bearer {self.landsat_key}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results"):
                            best_image = data["results"][0]
                            image_url = f"https://demo-landsat-image-{lat}-{lon}.jpg"
                            
                            return SatelliteImage(
                                url=image_url,
                                date=datetime.fromisoformat(best_image["date"]),
                                satellite="Landsat-8",
                                resolution=30.0,
                                cloud_coverage=best_image.get("cloud_cover", 0)
                            )
                    return None
                    
        except Exception as e:
            print(f"Landsat API error: {e}")
            return None
    
    def _calculate_bbox(self, lat: float, lon: float, radius_km: float) -> List[float]:
        lat_delta = radius_km / 111.0  
        lon_delta = radius_km / (111.0 * abs(np.cos(np.radians(lat))))
        
        return [
            lon - lon_delta,  
            lat - lat_delta,  
            lon + lon_delta,  
            lat + lat_delta   
        ]
    
    def _get_demo_image_url(self, lat: float, lon: float, image_type: str) -> str:
        lat_str = f"{lat:.2f}".replace(".", "").replace("-", "n")
        lon_str = f"{lon:.2f}".replace(".", "").replace("-", "w")
        
        if image_type == "recent":
            return f"https://demo-terramind-images.s3.amazonaws.com/recent_{lat_str}_{lon_str}.jpg"
        else:
            return f"https://demo-terramind-images.s3.amazonaws.com/historical_{lat_str}_{lon_str}.jpg"
    
    def _load_demo_images(self) -> Dict[str, Any]:
        return {
            "recent": {
                "url": "https://demo-terramind-images.s3.amazonaws.com/recent_demo.jpg",
                "date": datetime.now().isoformat(),
                "satellite": "Demo-Satellite",
                "resolution": 10.0,
                "cloud_coverage": 5.0
            },
            "historical": {
                "url": "https://demo-terramind-images.s3.amazonaws.com/historical_demo.jpg",
                "date": (datetime.now() - timedelta(days=365)).isoformat(),
                "satellite": "Demo-Satellite",
                "resolution": 10.0,
                "cloud_coverage": 8.0
            }
        }
    
    async def get_image_metadata(self, image_url: str) -> Dict[str, Any]:
        try:
            return {
                "url": image_url,
                "acquisition_date": datetime.now().isoformat(),
                "satellite": "Demo-Satellite",
                "resolution": 10.0,
                "cloud_coverage": 5.0,
                "bands": ["B02", "B03", "B04", "B08"],
                "processing_level": "L2A"
            }
        except Exception as e:
            return {
                "error": f"Failed to get metadata: {str(e)}",
                "url": image_url
            }
    
    async def search_images(self, lat: float, lon: float, radius_km: float, 
                          start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        try:
            images = []
            current_date = start_date
            
            while current_date <= end_date:
                if current_date.day % 5 == 0:  
                    images.append({
                        "date": current_date.isoformat(),
                        "url": self._get_demo_image_url(lat, lon, "search"),
                        "satellite": "Demo-Satellite",
                        "cloud_coverage": np.random.uniform(0, 30),
                        "resolution": 10.0
                    })
                
                current_date += timedelta(days=1)
            
            return images
            
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _validate_coordinates(self, lat: float, lon: float) -> bool:
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def _validate_radius(self, radius_km: float) -> bool:
        return 0.1 <= radius_km <= 100  
    
    async def get_available_dates(self, lat: float, lon: float) -> List[str]:
        try:
            dates = []
            base_date = datetime.now() - timedelta(days=365)
            
            for i in range(0, 365, 5):  
                date = base_date + timedelta(days=i)
                dates.append(date.isoformat())
            
            return dates
            
        except Exception as e:
            return [datetime.now().isoformat()]  