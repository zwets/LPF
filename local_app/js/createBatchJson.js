export function createBatchJson(input_list) {
    var JsonObject;
    JsonObject = JSON.parse(JSON.stringify(input_list));
    return JsonObject;
}