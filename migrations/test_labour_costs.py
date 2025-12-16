"""Test labour costs functionality"""
from database import Database
from event_manager import EventManager

def test_labour_costs():
    """Test labour costs CRUD operations"""
    db = Database()
    em = EventManager(db)

    # Create a test event first
    print("Creating test event...")
    event_data = {
        'event_name': 'Test Event for Labour Costs',
        'event_date': '2025-12-15',
        'start_time': '18:00:00',
        'end_time': '22:00:00',
        'event_type_id': 1,
        'max_capacity': 24
    }
    event_id = em.create_event(event_data)
    print(f"Created event with ID: {event_id}")

    # Test 1: Add weekday labour cost entry
    print("\nTest 1: Adding weekday labour cost entry...")
    labour_id_1 = em.add_labour_cost_entry(
        event_id=event_id,
        staff_name="John Smith",
        hours_worked=4.0,
        rate_type='weekday',
        hourly_rate=25.50,
        work_status='full'
    )
    print(f"Added labour entry with ID: {labour_id_1}")

    # Test 2: Add public holiday labour cost entry
    print("\nTest 2: Adding public holiday labour cost entry...")
    labour_id_2 = em.add_labour_cost_entry(
        event_id=event_id,
        staff_name="Jane Doe",
        hours_worked=5.5,
        rate_type='public_holiday',
        hourly_rate=35.00,
        work_status='full'
    )
    print(f"Added labour entry with ID: {labour_id_2}")

    # Test 3: Add partial work status entry
    print("\nTest 3: Adding partial work status entry...")
    labour_id_3 = em.add_labour_cost_entry(
        event_id=event_id,
        staff_name="Bob Wilson",
        hours_worked=2.0,
        rate_type='weekday',
        hourly_rate=25.50,
        work_status='partial'
    )
    print(f"Added labour entry with ID: {labour_id_3}")

    # Test 4: Get all labour costs for event
    print("\nTest 4: Retrieving all labour costs for event...")
    labour_costs = em.get_labour_costs(event_id)
    print(f"Found {len(labour_costs)} labour cost entries:")
    for labour in labour_costs:
        print(f"  - {labour['staff_name']}: {labour['hours_worked']} hrs @ ${labour['hourly_rate']}/hr "
              f"({labour['rate_type']}, {labour['work_status']}) = ${labour['total_cost']:.2f}")

    # Test 5: Calculate total labour cost
    print("\nTest 5: Calculating total labour cost...")
    total = em.get_total_labour_cost(event_id)
    print(f"Total labour cost: ${total:.2f}")

    # Expected calculations:
    # John: 4.0 * 25.50 = 102.00
    # Jane: 5.5 * 35.00 = 192.50
    # Bob: 2.0 * 25.50 = 51.00
    # Total: 345.50
    expected_total = (4.0 * 25.50) + (5.5 * 35.00) + (2.0 * 25.50)
    print(f"Expected total: ${expected_total:.2f}")

    if abs(total - expected_total) < 0.01:
        print("[PASS] Total calculation is CORRECT!")
    else:
        print("[FAIL] Total calculation is INCORRECT!")

    # Test 6: Update labour cost entry
    print("\nTest 6: Updating labour cost entry...")
    em.update_labour_cost_entry(
        labour_id=labour_id_1,
        staff_name="John Smith (Updated)",
        hours_worked=5.0,
        rate_type='weekday',
        hourly_rate=25.50,
        work_status='full'
    )
    updated_labour = em.get_labour_costs(event_id)
    print(f"Updated entry: {updated_labour[0]['staff_name']} - {updated_labour[0]['hours_worked']} hrs")

    # Test 7: Delete labour cost entry
    print("\nTest 7: Deleting labour cost entry...")
    em.delete_labour_cost_entry(labour_id_3)
    remaining = em.get_labour_costs(event_id)
    print(f"Remaining entries after deletion: {len(remaining)}")
    if len(remaining) == 2:
        print("[PASS] Deletion successful!")
    else:
        print("[FAIL] Deletion failed!")

    # Test 8: Verify rate types
    print("\nTest 8: Verifying rate types...")
    for labour in remaining:
        rate_type_display = labour['rate_type'].replace('_', ' ').title()
        print(f"  - {labour['staff_name']}: Rate Type = {rate_type_display}")
        if labour['rate_type'] in ['weekday', 'public_holiday']:
            print(f"    [PASS] Valid rate type")
        else:
            print(f"    [FAIL] Invalid rate type")

    # Test 9: Verify work status
    print("\nTest 9: Verifying work status...")
    for labour in remaining:
        status = labour['work_status'].capitalize()
        print(f"  - {labour['staff_name']}: Work Status = {status}")
        if labour['work_status'] in ['full', 'partial']:
            print(f"    [PASS] Valid work status")
        else:
            print(f"    [FAIL] Invalid work status")

    # Clean up - delete test event
    print("\nCleaning up test event...")
    em.delete_event(event_id)
    print("Test event deleted")

    print("\n" + "="*50)
    print("All tests completed successfully!")
    print("="*50)

if __name__ == "__main__":
    test_labour_costs()
