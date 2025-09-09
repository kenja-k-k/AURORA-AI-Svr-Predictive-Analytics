import base64
import csv
import os
from io import BytesIO

import grpc
from concurrent import futures
from datetime import datetime
import pandas as pd
from protos import service_pb2
from protos import service_pb2_grpc
import time
from insights import seasonal_emission_forecasts, predict_following_month_emission


class PredictionServiceServicer(service_pb2_grpc.PredictionAnalyticsServiceServicer):

    def UploadCSV(self, request, context):
        print("Upload request received")
        global csv_path, data
        csv_path = f"./dataset_file" + ".csv"

        with open(csv_path, "wb") as f:
            f.write(request.file_content)

        try:
            data = pd.read_csv(csv_path)
            return service_pb2.UploadCSVResponse(
                status="success",
                message=f"CSV uploaded and saved to {csv_path}"
            )
        except Exception as e:
            print("Error:", e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.UploadCSVResponse(status="failed", message="error")

    def GetSeasonalStats(self, request, context):

        global csv_path, data
        csv_path = fr".\dataset_file.csv"
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)

        if data.empty:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("No csv loaded. Use /set_csv/ before anything.")
            return service_pb2.GetSeasonalResponse()
        range_stats = seasonal_emission_forecasts(data, request.facility_name)

        if range_stats is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("No data available for this facility.")
            return service_pb2.GetSeasonalResponse()

        range_stats_output = {"points" : []}
        for idx in range_stats["season"].keys():
            point = {
                "season": range_stats["season"][idx],
                "column": range_stats["column"][idx],
                "median": range_stats["median"][idx],
                "lower":  range_stats["lower"][idx],
                "upper":  range_stats["upper"][idx]
            }
            range_stats_output["points"].append(point)

        range_stats_proto = service_pb2.ChartData(
            points = range_stats_output["points"],
        )

        return service_pb2.GetSeasonalResponse(
            chart_data = range_stats_proto
        )

    def GetPredictionStats(self, request, context):

        global csv_path, data
        csv_path = fr".\dataset_file.csv"
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)

        if data.empty:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("No csv loaded. Use /set_csv/ before anything.")
            return service_pb2.GetPredictionStatsResponse()

        prediction_stats = predict_following_month_emission(data, request.facility_name)

        if prediction_stats is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("No data available for this facility.")
            return service_pb2.GetPredictionStatsResponse()

       prediction_stats_proto = service_pb2.PredictionChartData(
            prediction_stats=prediction_stats,
        )

        return service_pb2.GetPredictionStatsResponse(
            chart_data=prediction_stats_proto
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_PredictionAnalyticsServiceServicer_to_server(PredictionServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting server on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep server alive for 1 day
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    serve()